"""
Servicio de Memoria Episódica a Largo Plazo.
Implementa la arquitectura avanzada de memoria:
  1. Extracción de Entidades (Fact Extraction) — hechos atómicos categorizados
  2. Actualización Semántica (UPSERT) — evita contradicciones
  3. Decaimiento por Relevancia (Time-Weighted Search) — prioriza recuerdos recientes
"""

import uuid
import json
import math
from datetime import datetime, timezone
from typing import Optional, List, Dict

from langchain_core.messages import HumanMessage
from app.core.chromadb_client import ChromaDBClient
from app.core.llm_service import LLMService
from app.core.logging import get_logger
from app.modules.agent.schemas import AgentState
from app.modules.agent.prompts import memory_extraction_prompt

logger = get_logger(__name__)

# Decay factor: memories lose ~50% relevance after 30 days
DECAY_LAMBDA = 0.023  # ln(2)/30 ≈ 0.023
SIMILARITY_THRESHOLD = 0.3  # Distance below which we consider a memory "same topic"


class MemoryService:
    """
    Servicio para manejar la Memoria Episódica del usuario a largo plazo.
    Extrae hechos categorizados y realiza Upsert semántico en ChromaDB.
    """

    @staticmethod
    async def extract_and_upsert_memory(state: AgentState) -> None:
        """
        Analiza los últimos mensajes, extrae preferencias/hechos categorizados
        y los guarda en la colección user_long_term_memory de ChromaDB.
        """
        user_id = state["user_id"]
        messages = state["messages"]

        # Solo procesamos si hay al menos un intercambio (user + ai)
        if len(messages) < 2:
            return

        # 1. Extraer último intercambio
        last_user_msg = ""
        last_ai_msg = ""
        for msg in reversed(messages):
            if msg.type == "human" and not last_user_msg:
                last_user_msg = msg.content
            elif msg.type == "ai" and not last_ai_msg:
                last_ai_msg = msg.content
            if last_user_msg and last_ai_msg:
                break

        if not last_user_msg:
            return

        logger.info(f"Iniciando extracción de memoria para {user_id}")

        # 2. Llamar al LLM para extraer hecho atómico categorizado
        prompt = memory_extraction_prompt.format(
            user_message=last_user_msg,
            assistant_message=last_ai_msg
        )

        llm_service = LLMService(session_id=state["session_id"], user_id=user_id)
        extraction = await llm_service.generate([HumanMessage(content=prompt)])
        extraction = extraction.strip()

        if extraction == "NULL" or not extraction or extraction.upper() == "NULL":
            logger.info("No se extrajo ninguna preferencia nueva.")
            return

        # 3. Parsear el JSON de extracción
        fact_data = _parse_extraction(extraction)
        if not fact_data:
            logger.info(f"Extracción no parseable, guardando como texto libre: {extraction[:80]}")
            fact_data = {
                "categoria": "general",
                "hecho": extraction,
                "entidad": "desconocido"
            }

        logger.info(f"Hecho extraído: {json.dumps(fact_data, ensure_ascii=False)}")

        # 4. Upsert semántico en ChromaDB
        client = ChromaDBClient()
        collection = client.episodic_memory
        if not collection:
            logger.error("No se pudo conectar a ChromaDB para guardar memoria episódica.")
            return

        fact_text = fact_data["hecho"]
        now_iso = datetime.now(timezone.utc).isoformat()

        # Buscar memorias similares para este usuario con la misma categoría
        try:
            results = collection.query(
                query_texts=[fact_text],
                n_results=3,
                where={"user_id": user_id}
            )
        except Exception as e:
            logger.warning(f"Error buscando memorias existentes: {e}")
            results = None

        memory_id = None
        if results and results.get("distances") and results["distances"][0]:
            for i, distance in enumerate(results["distances"][0]):
                existing_meta = results["metadatas"][0][i] if results["metadatas"][0] else {}
                existing_category = existing_meta.get("categoria", "")

                # Si la distancia es baja Y la categoría coincide, hacer upsert
                if distance < SIMILARITY_THRESHOLD and existing_category == fact_data["categoria"]:
                    memory_id = results["ids"][0][i]
                    logger.info(f"Actualizando memoria existente (dist={distance:.3f}): {memory_id}")
                    break

        if not memory_id:
            memory_id = str(uuid.uuid4())

        metadata = {
            "user_id": user_id,
            "session_id": state["session_id"],
            "categoria": fact_data["categoria"],
            "entidad": fact_data.get("entidad", ""),
            "timestamp": now_iso,
            "updated_at": now_iso,
        }

        collection.upsert(
            documents=[fact_text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        logger.info(f"Memoria guardada exitosamente para {user_id}: {fact_text[:60]}...")

    @staticmethod
    async def retrieve_relevant_memories(
        user_id: str, query: str, top_k: int = 3
    ) -> str:
        """
        Recupera los recuerdos más relevantes del usuario,
        aplicando Time-Weighted Decay para priorizar recuerdos recientes.
        """
        client = ChromaDBClient()
        collection = client.episodic_memory
        if not collection:
            return ""

        try:
            results = collection.query(
                query_texts=[query],
                n_results=top_k * 2,  # Traemos más para filtrar con decay
                where={"user_id": user_id}
            )
        except Exception as e:
            logger.warning(f"Error recuperando memorias para {user_id}: {e}")
            return ""

        if not results or not results.get("documents") or not results["documents"][0]:
            return ""

        # Aplicar Time-Weighted Decay
        scored_memories = []
        now = datetime.now(timezone.utc)

        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if results["distances"][0] else 1.0
            meta = results["metadatas"][0][i] if results["metadatas"][0] else {}

            # Calcular similarity (1 - distance para coseno)
            similarity = max(0, 1 - distance)

            # Calcular decay temporal
            timestamp_str = meta.get("timestamp", meta.get("updated_at", ""))
            if timestamp_str:
                try:
                    mem_time = datetime.fromisoformat(timestamp_str)
                    if mem_time.tzinfo is None:
                        mem_time = mem_time.replace(tzinfo=timezone.utc)
                    days_ago = (now - mem_time).total_seconds() / 86400
                    decay_factor = math.exp(-DECAY_LAMBDA * days_ago)
                except (ValueError, TypeError):
                    decay_factor = 0.5
            else:
                decay_factor = 0.5

            # Score final: similarity ponderada por decay temporal
            adjusted_score = similarity * decay_factor
            categoria = meta.get("categoria", "general")

            scored_memories.append({
                "text": doc,
                "score": adjusted_score,
                "categoria": categoria,
                "days_ago": days_ago if timestamp_str else -1,
            })

        # Ordenar por score descendente y tomar top_k
        scored_memories.sort(key=lambda x: x["score"], reverse=True)
        top_memories = scored_memories[:top_k]

        if not top_memories:
            return ""

        # Formatear para el prompt
        memory_lines = []
        for mem in top_memories:
            if mem["score"] > 0.1:  # Solo incluir memorias con score mínimo
                memory_lines.append(f"- [{mem['categoria']}] {mem['text']}")

        if not memory_lines:
            return ""

        return "\n".join(memory_lines)


def _parse_extraction(text: str) -> Optional[Dict[str, str]]:
    """Intenta parsear la extracción como JSON."""
    text = text.strip()
    # Limpiar posibles backticks o prefijos
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.startswith("json"):
            text = text[4:].strip()

    try:
        data = json.loads(text)
        if isinstance(data, dict) and "hecho" in data and "categoria" in data:
            return data
    except json.JSONDecodeError:
        pass

    return None
