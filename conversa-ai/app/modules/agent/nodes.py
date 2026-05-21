from typing import Dict, Any

from langchain_core.messages import HumanMessage, AIMessage

from app.core.llm_service import LLMService
from app.core.chromadb_client import ChromaDBClient
from app.core.logging import get_logger
from app.modules.agent.schemas import AgentState
from app.modules.agent.prompts import router_prompt, direct_response_prompt, gatekeeper_prompt, rag_response_prompt
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
    
    return {"messages": [new_message], "current_node": "gatekeeper_node"}


async def sql_node(state: AgentState) -> Dict[str, Any]:
    # Placeholder: En S1/S2 simplemente enviamos a generación directa para simular
    logger.info("sql_node no implementado aún, pasando a generación directa")
    return {"current_node": "direct_generate_node"}


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
    return {"current_node": "end"}
