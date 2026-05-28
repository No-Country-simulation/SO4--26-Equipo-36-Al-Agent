"""
Servicio de clasificación para el pipeline evaluador.

A) Análisis de sentimiento — HF Inference API (pysentimiento)
B) Extracción de intent — Groq LLM (backup para sesiones sin tags de intent)
"""

from __future__ import annotations

import asyncio
import json
from typing import Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.evaluator.schemas import SentimentLabel

logger = get_logger("evaluator.classifier")

# ── Mapeo de labels de pysentimiento → SentimentLabel ─────────────────────
_HF_LABEL_MAP: dict[str, SentimentLabel] = {
    "POS": SentimentLabel.POS,
    "NEG": SentimentLabel.NEG,
    "NEU": SentimentLabel.NEU,
    "POSITIVE": SentimentLabel.POS,
    "NEGATIVE": SentimentLabel.NEG,
    "NEUTRAL": SentimentLabel.NEU,
    "LABEL_0": SentimentLabel.NEG,
    "LABEL_1": SentimentLabel.NEU,
    "LABEL_2": SentimentLabel.POS,
}


class SentimentResult:
    """Resultado de una clasificación de sentimiento."""

    def __init__(self, label: SentimentLabel, score: float) -> None:
        self.label = label
        self.score = score


class SentimentClassifier:
    """Cliente async para la HF Inference API (pysentimiento).

    Usa un Semaphore para throttling y retry con backoff exponencial
    ante rate limits (HTTP 429).
    """

    HF_API_URL = "https://api-inference.huggingface.co/models/{model}"

    def __init__(self) -> None:
        self._semaphore = asyncio.Semaphore(settings.EVALUATOR_MAX_CONCURRENT)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy init del cliente HTTP."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.HF_API_TIMEOUT),
                headers={"Authorization": f"Bearer {settings.HF_API_TOKEN}"},
            )
        return self._client

    async def classify(self, text: str, lang: str = "es") -> SentimentResult:
        """Clasifica el sentimiento de un texto usando pysentimiento vía HF API.

        Args:
            text: Texto limpio del usuario (ya sin PII).
            lang: Código ISO del idioma ('es' o 'pt').

        Returns:
            SentimentResult con label y score.
        """
        if not text or not text.strip():
            return SentimentResult(label=SentimentLabel.NEU, score=0.5)

        model = (
            settings.HF_SENTIMENT_MODEL_ES
            if lang == "es"
            else settings.HF_SENTIMENT_MODEL_PT
        )
        url = self.HF_API_URL.format(model=model)

        # Truncar texto a 512 tokens aprox para el modelo
        truncated = text[:1500]

        async with self._semaphore:
            return await self._request_with_retry(url, truncated)

    async def _request_with_retry(
        self, url: str, text: str, max_retries: int = 3
    ) -> SentimentResult:
        """Realiza la request con exponential backoff ante 429/503."""
        client = await self._get_client()

        for attempt in range(max_retries):
            try:
                response = await client.post(url, json={"inputs": text})

                if response.status_code == 200:
                    return self._parse_response(response.json())

                if response.status_code in (429, 503):
                    wait = 2 ** (attempt + 1)
                    logger.warning(
                        f"HF API rate limit/loading (HTTP {response.status_code}), "
                        f"retry en {wait}s (intento {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(wait)
                    continue

                logger.error(
                    f"HF API error inesperado: HTTP {response.status_code} — "
                    f"{response.text[:200]}"
                )
                return SentimentResult(label=SentimentLabel.NEU, score=0.5)

            except httpx.TimeoutException:
                logger.warning(f"HF API timeout, intento {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                continue
            except Exception as e:
                logger.error(f"Error inesperado en clasificación: {e}")
                return SentimentResult(label=SentimentLabel.NEU, score=0.5)

        logger.error("HF API: agotados los reintentos, devolviendo NEU por defecto")
        return SentimentResult(label=SentimentLabel.NEU, score=0.5)

    def _parse_response(self, data: list | dict) -> SentimentResult:
        """Parsea la respuesta de la HF Inference API."""
        try:
            # La API retorna [[{label, score}, ...]] o [{label, score}, ...]
            results = data[0] if isinstance(data[0], list) else data
            if not results:
                return SentimentResult(label=SentimentLabel.NEU, score=0.5)

            top = max(results, key=lambda x: x.get("score", 0))
            raw_label = top.get("label", "NEU").upper()
            label = _HF_LABEL_MAP.get(raw_label, SentimentLabel.NEU)
            score = float(top.get("score", 0.5))
            return SentimentResult(label=label, score=score)

        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error parseando respuesta HF: {e} — data: {data}")
            return SentimentResult(label=SentimentLabel.NEU, score=0.5)

    async def classify_batch(
        self, texts: list[tuple[str, str]]
    ) -> list[SentimentResult]:
        """Clasifica múltiples textos en paralelo controlado.

        Args:
            texts: Lista de tuplas (text, lang_iso).

        Returns:
            Lista de SentimentResult en el mismo orden.
        """
        tasks = [self.classify(text, lang) for text, lang in texts]
        return await asyncio.gather(*tasks)

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


class IntentExtractor:
    """Extrae la intención dominante de una sesión usando Groq LLM.

    Usa como fallback cuando la sesión no tiene tags de intent
    asignados en el OLTP.
    """

    def __init__(self) -> None:
        from app.modules.evaluator.prompts import (
            INTENT_EXTRACTION_SYSTEM_PROMPT,
            INTENT_EXTRACTION_USER_PROMPT,
            VALID_INTENTS,
        )
        self._system_prompt = INTENT_EXTRACTION_SYSTEM_PROMPT
        self._user_prompt = INTENT_EXTRACTION_USER_PROMPT
        self._valid_intents = VALID_INTENTS

    async def extract_intent(self, user_text: str) -> tuple[str, str]:
        """Extrae el intent principal del texto concatenado del usuario.

        Returns:
            Tupla (intent_name, intent_category).
        """
        if not user_text or not user_text.strip():
            return "intent_desconocido", "general"

        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            from app.core.llm_service import LLMService

            llm_service = LLMService()
            messages = [
                SystemMessage(content=self._system_prompt),
                HumanMessage(content=self._user_prompt.format(
                    user_text=user_text[:1000]
                )),
            ]
            response = await llm_service.generate(messages)
            return self._parse_intent(response)

        except Exception as e:
            logger.error(f"Error extrayendo intent vía LLM: {e}")
            return "intent_desconocido", "general"

    def _parse_intent(self, response: str) -> tuple[str, str]:
        """Parsea el JSON de respuesta del LLM."""
        try:
            clean = response.strip()
            # Buscar JSON en la respuesta
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(clean[start:end])
                intent = data.get("intent", "intent_desconocido")
                if intent in self._valid_intents:
                    return intent, self._valid_intents[intent]
            return "intent_desconocido", "general"
        except (json.JSONDecodeError, AttributeError):
            return "intent_desconocido", "general"


# ── Singletons ────────────────────────────────────────────────────────────

sentiment_classifier = SentimentClassifier()
intent_extractor = IntentExtractor()
