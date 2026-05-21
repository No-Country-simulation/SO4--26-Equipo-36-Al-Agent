from typing import Dict, Any

from langchain_core.messages import HumanMessage, AIMessage

from app.core.llm_service import LLMService
from app.core.chromadb_client import ChromaDBClient
from app.core.logging import get_logger
from app.modules.agent.schemas import AgentState
from app.modules.agent.prompts import router_prompt, direct_response_prompt, gatekeeper_prompt, rag_response_prompt
from app.modules.agent.db_service import DBService
from rank_bm25 import BM25Okapi

logger = get_logger(__name__)


async def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    Evalúa la última interacción y decide a qué nodo enrutar (RAG, SQL, DIRECT).
    """
    last_message = state["messages"][-1].content
    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])
    
    prompt = router_prompt.format(user_message=last_message)
    response_text = await llm_service.generate([HumanMessage(content=prompt)])
    
    decision = response_text.strip().upper()
    if "RAG" in decision:
        route = "rag_node"
    elif "SQL" in decision:
        route = "sql_node"
    else:
        route = "direct_generate_node"
        
    logger.info(f"Supervisor ruteando a: {route}")
    
    return {"current_node": route}


async def direct_generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Genera una respuesta directa cuando no se necesitan herramientas RAG o SQL.
    """
    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])
    
    formatted_messages = await direct_response_prompt.aformat_messages(messages=state["messages"])
    response_text = await llm_service.generate(formatted_messages)
    
    # Añadir la respuesta del asistente a los mensajes
    new_message = AIMessage(content=response_text)
    
    # Persistir en DB
    await DBService.save_message(state["session_id"], role_id=2, content=response_text)
    
    return {"messages": [new_message], "current_node": "gatekeeper_node"}


async def rag_node(state: AgentState) -> Dict[str, Any]:
    """
    Recupera contexto de la base de conocimiento usando búsqueda híbrida (Densa + BM25).
    """
    logger.info("Ejecutando nodo RAG (Hybrid Search)")
    user_message = state["messages"][-1].content
    
    # 1. Búsqueda Densa (ChromaDB)
    client = ChromaDBClient()
    collection = client.knowledge_base
    if not collection:
        logger.error("No se pudo conectar a ChromaDB")
        return {"current_node": "direct_generate_node", "context": ""}
        
    results = collection.query(
        query_texts=[user_message],
        n_results=10 # Traemos top 10 para hacer reranking
    )
    
    documents = results.get("documents", [[]])[0]
    
    if not documents:
        return {"current_node": "rag_generate_node", "context": ""}
        
    # 2. Búsqueda Léxica (BM25) para Reranking
    tokenized_corpus = [doc.split(" ") for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = user_message.split(" ")
    
    # Obtener el top 3 de los 10 recuperados según BM25
    top_n = 3
    reranked_docs = bm25.get_top_n(tokenized_query, documents, n=top_n)
    
    context = "\n---\n".join(reranked_docs)
    
    return {"current_node": "rag_generate_node", "context": context}


async def rag_generate_node(state: AgentState) -> Dict[str, Any]:
    """Genera la respuesta usando el contexto del RAG."""
    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])
    
    context = state.get("context", "")
    formatted_messages = await rag_response_prompt.aformat_messages(
        context=context,
        messages=state["messages"]
    )
    
    response_text = await llm_service.generate(formatted_messages)
    new_message = AIMessage(content=response_text)
    
    # Persistir en DB
    await DBService.save_message(state["session_id"], role_id=2, content=response_text)
    
    return {"messages": [new_message], "current_node": "gatekeeper_node"}


from app.modules.agent.tools import FINTECH_TOOLS
from app.modules.agent.otp_service import OTPService

async def sql_node(state: AgentState) -> Dict[str, Any]:
    """
    Ejecuta herramientas transaccionales. Requiere autenticación OTP previa.
    """
    logger.info("Ejecutando nodo SQL (Tool Executor)")
    
    if not state.get("is_authenticated", False):
        logger.warning("Usuario no autenticado intentando acceder a nodo SQL. Ruteando a step-up auth.")
        return {"current_node": "step_up_auth_node"}
        
    user_message = state["messages"][-1].content.lower()
    user_id = state["user_id"]
    
    # En un entorno real, el LLM clasificaría la herramienta a usar
    # Acá usamos una heurística básica para el MVP
    if "saldo" in user_message:
        result = await FINTECH_TOOLS["get_account_balance"](user_id)
    elif "movimiento" in user_message or "transacc" in user_message:
        result = await FINTECH_TOOLS["get_recent_transactions"](user_id)
    elif "tarjeta" in user_message:
        result = await FINTECH_TOOLS["get_card_status"](user_id)
    else:
        result = "No entiendo qué operación querés realizar."
        
    # Agregamos el resultado como mensaje de sistema o IA
    new_message = AIMessage(content=result)
    
    await DBService.save_message(state["session_id"], role_id=2, content=result)
    
    return {"messages": [new_message], "current_node": "end"}


async def step_up_auth_node(state: AgentState) -> Dict[str, Any]:
    """
    Gestiona el desafío OTP.
    Si el usuario ingresa un código, lo valida.
    Si no, genera uno nuevo y pide que lo ingrese.
    """
    logger.info("Ejecutando nodo Step-Up Auth")
    user_message = state["messages"][-1].content.strip()
    user_id = state["user_id"]
    phone_number = user_id.replace("wa_", "") # Extraer número simulado
    
    # Si el mensaje es numérico y de 6 dígitos, asumimos que es el código
    if user_message.isdigit() and len(user_message) == 6:
        is_valid, msg = OTPService.validate_otp(user_id, user_message)
        if is_valid:
            logger.info(f"OTP validado exitosamente para {user_id}")
            return {"is_authenticated": True, "current_node": "sql_node"}
        else:
            logger.warning(f"Fallo validación OTP para {user_id}: {msg}")
            new_message = AIMessage(content=msg)
            await DBService.save_message(state["session_id"], role_id=2, content=msg)
            return {"messages": [new_message], "current_node": "end"}
            
    # Si no ingresó código, generamos uno nuevo
    OTPService.generate_and_send_otp(user_id, phone_number)
    msg = "Por seguridad, necesitamos verificar tu identidad. Te acabamos de enviar un código de 6 dígitos. Por favor, ingresalo aquí:"
    new_message = AIMessage(content=msg)
    
    await DBService.save_message(state["session_id"], role_id=2, content=msg)
    
    return {"messages": [new_message], "current_node": "end"}


async def gatekeeper_node(state: AgentState) -> Dict[str, Any]:
    """
    Audita la respuesta para verificar que no haya alucinaciones.
    Si falla, incrementa el retry_count y solicita regeneración.
    """
    if len(state["messages"]) < 2:
        return {"current_node": "end"}
        
    last_ai_message = state["messages"][-1].content
    user_message = state["messages"][-2].content if len(state["messages"]) >= 2 else ""
    
    llm_service = LLMService(session_id=state["session_id"], user_id=state["user_id"])
    
    context = state.get("context", "No context applied")
    
    prompt = gatekeeper_prompt.format(
        user_message=user_message,
        context=context,
        generated_response=last_ai_message
    )
    
    response_text = await llm_service.generate([HumanMessage(content=prompt)])
    decision = response_text.strip().upper()
    
    if "REJECT" in decision and state.get("retry_count", 0) < 3:
        logger.warning(f"Gatekeeper rechazó la respuesta. Reintentando ({state.get('retry_count', 0) + 1}/3)")
        # Quitar el mensaje rechazado
        if state.get("context") is not None:
            retry_node = "rag_generate_node"
        else:
            retry_node = "direct_generate_node"
            
        return {"messages": [], "retry_count": state.get("retry_count", 0) + 1, "current_node": retry_node}
        
    logger.info("Gatekeeper aprobó la respuesta.")
    return {"current_node": "update_memory_node"}


from app.modules.agent.memory_service import MemoryService

async def update_memory_node(state: AgentState) -> Dict[str, Any]:
    """
    Nodo final que extrae y persiste la memoria episódica antes de terminar.
    """
    await MemoryService.extract_and_upsert_memory(state)
    return {"current_node": "end"}
