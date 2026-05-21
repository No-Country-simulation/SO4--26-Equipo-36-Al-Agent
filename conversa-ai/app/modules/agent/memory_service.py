import uuid
from typing import Optional

from langchain_core.messages import HumanMessage
from app.core.chromadb_client import ChromaDBClient
from app.core.llm_service import LLMService
from app.core.logging import get_logger
from app.modules.agent.schemas import AgentState

logger = get_logger(__name__)


class MemoryService:
    """
    Servicio para manejar la Memoria Episódica del usuario a largo plazo.
    Extrae hechos de la conversación y realiza un Upsert semántico en ChromaDB.
    """
    
    @staticmethod
    async def extract_and_upsert_memory(state: AgentState):
        """
        Analiza los últimos mensajes, extrae preferencias/hechos y los guarda
        en la colección user_long_term_memory de ChromaDB.
        """
        user_id = state["user_id"]
        messages = state["messages"]
        
        # Solo procesamos si hay al menos un intercambio (user + ai)
        if len(messages) < 2:
            return
            
        logger.info(f"Iniciando extracción de memoria para {user_id}")
        
        # 1. Armar el texto del último intercambio
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
            
        # 2. Llamar al LLM para extraer el hecho atómico
        prompt = f"""Sos un extractor de preferencias de usuario.
Tu objetivo es analizar la siguiente conversación y extraer UNA ÚNICA preferencia, hecho o dato relevante que el usuario haya mencionado sobre sí mismo (ej. "Prefiere bajo riesgo", "Tiene hijos", "No le gusta usar tarjetas físicas").
Si no hay ningún dato personal o preferencia relevante, responde exactamente: NULL.

Usuario: {last_user_msg}
Asistente: {last_ai_msg}

Extracción (o NULL):"""

        llm_service = LLMService(session_id=state["session_id"], user_id=user_id)
        extraction = await llm_service.generate([HumanMessage(content=prompt)])
        extraction = extraction.strip()
        
        if extraction == "NULL" or not extraction:
            logger.info("No se extrajo ninguna preferencia nueva.")
            return
            
        logger.info(f"Hecho extraído: {extraction}")
        
        # 3. Upsert en ChromaDB
        client = ChromaDBClient()
        collection = client.episodic_memory
        if not collection:
            logger.error("No se pudo conectar a ChromaDB para guardar memoria episódica.")
            return
            
        # Buscar memorias similares para este usuario (Upsert semántico)
        results = collection.query(
            query_texts=[extraction],
            n_results=1,
            where={"user_id": user_id}  # Filtrado ESTRICTO por tenant
        )
        
        memory_id = None
        if results and results.get("distances") and results["distances"][0]:
            distance = results["distances"][0][0]
            # Si la similitud es muy alta (distancia muy baja), pisamos el vector viejo
            if distance < 0.2: 
                memory_id = results["ids"][0][0]
                logger.info(f"Actualizando memoria existente: {memory_id}")
                
        if not memory_id:
            memory_id = str(uuid.uuid4())
            
        collection.upsert(
            documents=[extraction],
            metadatas=[{"user_id": user_id, "session_id": state["session_id"]}],
            ids=[memory_id]
        )
        logger.info(f"Memoria guardada exitosamente para {user_id}")
