import asyncio
from typing import Any, List, Optional

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langchain_cerebras import ChatCerebras

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    """
    Servicio LLM centralizado con lógica de Fallback Circular y Exponential Backoff.
    Proveedor principal: Groq.
    Proveedor de respaldo: Cerebras.
    """

    def __init__(self, session_id: Optional[str] = None, user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.logger = get_logger(__name__, session_id=session_id, user_id=user_id)

        # Configuración de Groq
        self.groq_model = None
        if settings.GROQ_API_KEY:
            self.groq_model = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model_name=settings.LLM_MODEL_NAME,
                temperature=0.1,
                max_retries=0, # Desactivamos retries internos para manejarlos nosotros
            )

        # Configuración de Cerebras
        self.cerebras_model = None
        if settings.CEREBRAS_API_KEY:
            self.cerebras_model = ChatCerebras(
                api_key=settings.CEREBRAS_API_KEY,
                model=settings.CEREBRAS_MODEL_NAME,
                temperature=0.1,
                max_retries=0,
            )

    async def _invoke_with_backoff(self, model: Any, messages: List[BaseMessage], provider_name: str, max_attempts: int = 3) -> Optional[BaseMessage]:
        """Ejecuta el modelo con backoff exponencial."""
        base_delay = 1.0
        
        for attempt in range(1, max_attempts + 1):
            try:
                self.logger.info(f"Invocando {provider_name} (Intento {attempt}/{max_attempts})...")
                # Las variables de entorno de LangSmith ya se encargan de trazar la ejecución si están configuradas
                response = await model.ainvoke(messages)
                return response
            except Exception as e:
                self.logger.warning(
                    f"Fallo al invocar {provider_name} (Intento {attempt}/{max_attempts}): {str(e)}"
                )
                if attempt == max_attempts:
                    self.logger.error(f"{provider_name} falló tras {max_attempts} intentos.")
                    return None
                
                delay = base_delay * (2 ** (attempt - 1))
                await asyncio.sleep(delay)
        return None

    async def generate(self, messages: List[BaseMessage]) -> str:
        """
        Genera una respuesta invocando primero a Groq, y si falla, a Cerebras.
        Garantiza que no lanza excepciones no controladas.
        """
        response_msg = None

        # 1. Intentar con Groq (Principal)
        if self.groq_model:
            response_msg = await self._invoke_with_backoff(self.groq_model, messages, "Groq")

        # 2. Intentar con Cerebras (Fallback)
        if not response_msg and self.cerebras_model:
            self.logger.warning("Groq falló o no está configurado. Rotando a Cerebras (Fallback).")
            response_msg = await self._invoke_with_backoff(self.cerebras_model, messages, "Cerebras")

        # 3. Contingencia Absoluta
        if not response_msg:
            self.logger.error("Todos los proveedores LLM fallaron. Retornando mensaje de contingencia.")
            return "En este momento estoy experimentando dificultades técnicas. Por favor, intentá de nuevo en unos minutos."

        return str(response_msg.content)
