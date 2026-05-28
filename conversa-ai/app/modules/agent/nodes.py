"""
Nodos del StateGraph de LangGraph para el Agente Conversacional ConversaAI.
Cada nodo es una función async que recibe el AgentState y retorna un dict parcial.
"""

import re
import random
import asyncio
from typing import Dict, Any

from langchain_core.messages import HumanMessage, AIMessage
from rank_bm25 import BM25Okapi

from app.core.llm_service import LLMService
from app.core.chromadb_client import ChromaDBClient
from app.core.logging import get_logger
from app.modules.agent.schemas import AgentState
from app.modules.agent.prompts import (
    router_prompt,
    greeting_prompt,
    out_of_scope_prompt,
    gatekeeper_prompt,
    rag_response_prompt,
    memory_extraction_prompt,
)
from app.modules.agent.db_service import DBService

logger = get_logger(__name__)


def sanitize_markdown(text: str) -> str:
    """Limpia caracteres de markdown para presentación limpia al usuario."""
    # Eliminar headers markdown
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Eliminar bold/italic
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Convertir viñetas markdown a texto limpio
    text = re.sub(r'^\s*[-*+]\s+', '• ', text, flags=re.MULTILINE)
    # Eliminar backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Eliminar posibles etiquetas HTML generadas por el LLM
    text = re.sub(r'<[^>]+>', '', text)
    # Limpiar líneas vacías excesivas
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ============================================================================
# SUPERVISOR — Router inteligente
# ============================================================================
async def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    Evalúa la intención del usuario y enruta a:
    - rag_node: consultas informativas sobre Conversa Pay
    - sql_node: consultas transaccionales (saldo, movimientos, tarjetas)
    - greeting_node: saludos y despedidas
    - out_of_scope_node: preguntas fuera de contexto
    """
    last_message = state["messages"][-1].content
    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])

    prompt = router_prompt.format(user_message=last_message)
    response_text = await llm_service.generate([HumanMessage(content=prompt)])

    decision = response_text.strip().upper()

    if "OUT_OF_SCOPE" in decision:
        route = "out_of_scope_node"
    elif "RAG" in decision:
        route = "rag_node"
    elif "SQL" in decision:
        route = "sql_node"
    elif "GREETING" in decision:
        route = "greeting_node"
    else:
        # Default: si no clasificó bien, intentar RAG para que el contexto decida
        route = "rag_node"

    logger.info(f"Supervisor ruteando a: {route} (decision: {decision})")
    return {"current_node": route}


# ============================================================================
# GREETING — Saludos y despedidas
# ============================================================================
async def greeting_node(state: AgentState) -> Dict[str, Any]:
    """Genera respuesta amigable a saludos, despedidas y agradecimientos."""
    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])

    formatted_messages = await greeting_prompt.aformat_messages(messages=state["messages"])
    response_text = await llm_service.generate(formatted_messages)
    response_text = sanitize_markdown(response_text)

    user_msg = state["messages"][-1].content.strip().lower()
    negative_closures = ["no", "no gracias", "no, gracias", "nada mas", "nada más", "eso es todo", "ninguna otra cosa", "no necesito nada mas", "no necesito nada más"]

    is_finished = False
    
    if "[FAREWELL]" in response_text or user_msg in negative_closures:
        response_text = response_text.replace("[FAREWELL]", "").strip()
        
        # Override response if the LLM failed to properly bid farewell on a negative closure
        if user_msg in negative_closures and "¿Podrías calificar" not in response_text:
            response_text = "Fue un gusto ayudarte. ¡Que tengas un buen día! ¿Podrías calificar mi atención?"
        elif "¿Podrías calificar mi atención?" not in response_text:
            response_text += " ¿Podrías calificar mi atención?"
            
        is_finished = True

    new_message = AIMessage(content=response_text)
    await DBService.save_message(state["session_id"], role_id=2, content=response_text, message_id=state.get("ui_msg_id"))

    return {
        "messages": [new_message],
        "is_finished": is_finished,
        "current_node": "update_memory_node"
    }


# ============================================================================
# OUT OF SCOPE — Rechazo amigable de preguntas fuera de contexto
# ============================================================================
async def out_of_scope_node(state: AgentState) -> Dict[str, Any]:
    """Rechaza preguntas fuera de contexto con sugerencias de temas válidos."""
    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])
    user_message = state["messages"][-1].content

    prompt = out_of_scope_prompt.format(user_message=user_message)
    response_text = await llm_service.generate([HumanMessage(content=prompt)])
    response_text = sanitize_markdown(response_text)

    new_message = AIMessage(content=response_text)
    await DBService.save_message(state["session_id"], role_id=2, content=response_text, message_id=state.get("ui_msg_id"))

    return {"messages": [new_message], "current_node": "update_memory_node"}


# ============================================================================
# RAG NODE — Búsqueda Híbrida (Q2Q + Dense + BM25 Rerank)
# ============================================================================
async def rag_node(state: AgentState) -> Dict[str, Any]:
    """
    Recupera contexto usando búsqueda híbrida en 3 pasos:
    1. Q2Q Search: Busca preguntas similares en el índice Q2Q
    2. Dense Search: Busca chunks similares en knowledge_base
    3. BM25 Rerank: Fusiona y re-rankea con BM25
    """
    logger.info("Ejecutando nodo RAG (Hybrid Search: Q2Q + Dense + BM25)")
    user_message = state["messages"][-1].content

    client = ChromaDBClient()
    kb_collection = client.knowledge_base
    q2q_collection = client.q2q_index

    all_candidate_docs = []
    doc_sources = {}  # Para deduplicación

    # 1. Q2Q Search — Buscar preguntas similares
    if q2q_collection:
        try:
            q2q_results = await asyncio.to_thread(
                q2q_collection.query,
                query_texts=[user_message],
                n_results=5
            )
            if q2q_results and q2q_results.get("metadatas"):
                for i, meta in enumerate(q2q_results["metadatas"][0]):
                    original = meta.get("original_content", "")
                    if original and original not in doc_sources:
                        all_candidate_docs.append(original)
                        doc_sources[original] = f"q2q_{i}"
                        logger.info(f"  Q2Q hit: {q2q_results['documents'][0][i][:60]}...")
        except Exception as e:
            logger.warning(f"Error en Q2Q search: {e}")

    # 2. Dense Search — Buscar chunks directamente
    if kb_collection:
        try:
            dense_results = await asyncio.to_thread(
                kb_collection.query,
                query_texts=[user_message],
                n_results=5
            )
            if dense_results and dense_results.get("documents"):
                for i, doc in enumerate(dense_results["documents"][0]):
                    if doc and doc not in doc_sources:
                        all_candidate_docs.append(doc)
                        doc_sources[doc] = f"dense_{i}"
        except Exception as e:
            logger.warning(f"Error en Dense search: {e}")

    if not all_candidate_docs:
        logger.warning("No se encontró contexto en ninguna colección")
        return {"current_node": "rag_generate_node", "context": ""}

    # 3. BM25 Reranking — Fusionar y ordenar por relevancia
    try:
        tokenized_corpus = [doc.lower().split() for doc in all_candidate_docs]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = user_message.lower().split()

        top_n = min(3, len(all_candidate_docs))
        reranked_docs = bm25.get_top_n(tokenized_query, all_candidate_docs, n=top_n)
    except Exception as e:
        logger.warning(f"Error en BM25 reranking, usando docs sin rerank: {e}")
        reranked_docs = all_candidate_docs[:3]

    context = "\n---\n".join(reranked_docs)
    logger.info(f"Contexto final: {len(reranked_docs)} docs, {len(context)} chars")

    return {"current_node": "rag_generate_node", "context": context}


# ============================================================================
# RAG GENERATE — Genera respuesta usando contexto RAG
# ============================================================================
async def rag_generate_node(state: AgentState) -> Dict[str, Any]:
    """Genera la respuesta usando el contexto del RAG + memoria del usuario."""
    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])

    context = state.get("context", "")
    user_memories = state.get("user_memories", "")

    # Agregar contexto de memoria si existe
    memory_context = ""
    if user_memories:
        memory_context = f"""
Información recordada sobre este usuario (memoria a largo plazo):
{user_memories}
Usá esta información para personalizar tu respuesta si es relevante."""

    formatted_messages = await rag_response_prompt.aformat_messages(
        context=context if context else "No se encontró contexto relevante en la base de conocimiento.",
        memory_context=memory_context,
        messages=state["messages"]
    )

    response_text = await llm_service.generate(formatted_messages)
    response_text = sanitize_markdown(response_text)

    new_message = AIMessage(content=response_text)
    await DBService.save_message(state["session_id"], role_id=2, content=response_text, message_id=state.get("ui_msg_id"))

    return {"messages": [new_message], "current_node": "gatekeeper_node"}


# ============================================================================
# SQL NODE — Ejecuta herramientas transaccionales
# ============================================================================
from app.modules.agent.tools import FINTECH_TOOLS

async def sql_node(state: AgentState) -> Dict[str, Any]:
    """
    Ejecuta herramientas transaccionales (solo lectura).
    Requiere autenticación OTP previa.
    """
    logger.info("Ejecutando nodo SQL (Tool Executor)")

    if not state.get("is_authenticated", False):
        logger.warning("Usuario no autenticado en nodo SQL. Ruteando a step-up auth.")
        return {"current_node": "step_up_auth_node"}

    user_message = state["messages"][-1].content.lower()
    user_id = state["user_id"]

    # Heurística de clasificación de herramientas
    if any(w in user_message for w in ["saldo", "balance", "cuánto tengo", "cuanto tengo", "plata"]):
        result = await FINTECH_TOOLS["get_account_balance"](user_id)
    elif any(w in user_message for w in ["movimiento", "transacc", "últim", "historial", "gast"]):
        result = await FINTECH_TOOLS["get_recent_transactions"](user_id)
    elif any(w in user_message for w in ["tarjeta", "card", "visa", "master", "débito", "crédito"]):
        result = await FINTECH_TOOLS["get_card_status"](user_id)
    else:
        result = ("Puedo ayudarte a consultar tu saldo, ver tus últimos movimientos "
                  "o verificar el estado de tus tarjetas. ¿Qué necesitás?")

    result = sanitize_markdown(result)
    new_message = AIMessage(content=result)
    await DBService.save_message(state["session_id"], role_id=2, content=result, message_id=state.get("ui_msg_id"))

    return {"messages": [new_message], "current_node": "update_memory_node"}


# ============================================================================
# STEP-UP AUTH — Autenticación real con OTP por Email
# ============================================================================
from app.modules.agent.otp_service import OTPService

async def step_up_auth_node(state: AgentState) -> Dict[str, Any]:
    """
    Gestiona el flujo de autenticación OTP conversacional:
    1. Pide email al usuario
    2. Busca en DB, genera OTP y envía por email real
    3. Valida el código ingresado
    """
    logger.info("Ejecutando nodo Step-Up Auth")
    user_message = state["messages"][-1].content.strip()
    user_id = state["user_id"]

    # Caso 1: El usuario ingresó un código de 6 dígitos
    if user_message.isdigit() and len(user_message) == 6:
        is_valid, msg = await OTPService.validate_otp(user_id, user_message)
        if is_valid:
            logger.info(f"OTP validado exitosamente para {user_id}")
            response = "Identidad verificada correctamente. Ahora puedo acceder a tu información financiera. ¿Qué necesitás consultar?"
            new_message = AIMessage(content=response)
            await DBService.save_message(state["session_id"], role_id=2, content=response, message_id=state.get("ui_msg_id"))
            return {
                "messages": [new_message],
                "is_authenticated": True,
                "current_node": "sql_node"
            }
        else:
            new_message = AIMessage(content=msg)
            await DBService.save_message(state["session_id"], role_id=2, content=msg, message_id=state.get("ui_msg_id"))
            return {"messages": [new_message], "current_node": "end"}

    # Caso 2: El usuario ingresó un email → buscar y enviar OTP
    if "@" in user_message and "." in user_message:
        email = user_message.lower().strip()
        user_data = await DBService.find_user_by_email(email)

        if not user_data:
            msg = ("No encontramos una cuenta registrada con ese email. "
                   "Si querés, puedo ayudarte con información general sobre nuestros productos y servicios.")
            new_message = AIMessage(content=msg)
            await DBService.save_message(state["session_id"], role_id=2, content=msg, message_id=state.get("ui_msg_id"))
            return {"messages": [new_message], "current_node": "end"}

        # Generar y enviar OTP real
        success = await OTPService.generate_and_send_otp(
            user_id=user_id,
            email=email,
            user_name=user_data.get("full_name", "")
        )

        if success:
            msg = (f"Te envié un código de verificación de 6 dígitos a {email}. "
                   "Revisá tu bandeja de entrada (y spam) e ingresá el código aquí:")
        else:
            msg = ("Hubo un problema al enviar el código de verificación. "
                   "Por favor, intentá de nuevo en unos minutos.")

        new_message = AIMessage(content=msg)
        await DBService.save_message(state["session_id"], role_id=2, content=msg, message_id=state.get("ui_msg_id"))
        return {
            "messages": [new_message],
            "user_email": email,
            "otp_pending": True,
            "current_node": "end"
        }

    # Caso 3: Primera interacción → pedir email
    msg = ("Para acceder a tu información financiera, necesito verificar tu identidad. "
           "Por favor, ingresá el email con el que te registraste en Conversa Pay:")
    new_message = AIMessage(content=msg)
    await DBService.save_message(state["session_id"], role_id=2, content=msg, message_id=state.get("ui_msg_id"))
    return {"messages": [new_message], "otp_pending": True, "current_node": "end"}


# ============================================================================
# GATEKEEPER — Auditor de alucinaciones y calidad
# ============================================================================
async def gatekeeper_node(state: AgentState) -> Dict[str, Any]:
    """
    Audita la respuesta para verificar que:
    - No haya alucinaciones
    - Responda la pregunta del usuario
    - No contenga markdown crudo
    - Esté enfocada en el negocio
    """
    if len(state["messages"]) < 2:
        return {"current_node": "update_memory_node"}

    last_ai_message = state["messages"][-1].content
    # Buscar el último mensaje del usuario (puede no ser [-2] si hay mensajes del sistema)
    user_message = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human":
            user_message = msg.content
            break

    if not user_message:
        return {"current_node": "update_memory_node"}

    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])
    context = state.get("context", "No context applied")

    prompt = gatekeeper_prompt.format(
        user_message=user_message,
        context=context,
        generated_response=last_ai_message
    )

    response_text = await llm_service.generate([HumanMessage(content=prompt)])
    decision = response_text.strip().upper()

    if "REJECT" in decision and state.get("retry_count", 0) < 2:
        logger.warning(f"Gatekeeper rechazó la respuesta. Reintentando ({state.get('retry_count', 0) + 1}/2)")
        retry_node = "rag_generate_node" if state.get("context") else "greeting_node"
        return {
            "messages": [],
            "retry_count": state.get("retry_count", 0) + 1,
            "current_node": retry_node
        }

    # Si llega acá, aprobado (o agotó retries, dejamos pasar igual)
    if "REJECT" in decision:
        logger.warning("Gatekeeper rechazó pero se agotaron retries. Dejando pasar.")

    logger.info("Gatekeeper aprobó la respuesta.")
    return {"current_node": "update_memory_node"}


# ============================================================================
# UPDATE MEMORY — Extrae y persiste memoria episódica
# ============================================================================
from app.modules.agent.memory_service import MemoryService

async def update_memory_node(state: AgentState) -> Dict[str, Any]:
    """Nodo final que extrae y persiste la memoria episódica antes de terminar."""
    try:
        await MemoryService.extract_and_upsert_memory(state)
    except Exception as e:
        logger.error(f"Error en update_memory_node: {e}")
    return {"current_node": "end"}
