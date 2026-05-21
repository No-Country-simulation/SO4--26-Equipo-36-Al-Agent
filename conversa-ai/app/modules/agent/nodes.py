from typing import Dict, Any

from langchain_core.messages import HumanMessage, AIMessage

from app.core.llm_service import LLMService
from app.core.logging import get_logger
from app.modules.agent.schemas import AgentState
from app.modules.agent.prompts import router_prompt, direct_response_prompt, gatekeeper_prompt

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


# Placeholders para los nodos que se implementarán en la Iteración 2 y 3
async def rag_node(state: AgentState) -> Dict[str, Any]:
    # Placeholder: En S1 simplemente enviamos a generación directa para simular
    logger.info("rag_node no implementado aún, pasando a generación directa")
    return {"current_node": "direct_generate_node"}

async def sql_node(state: AgentState) -> Dict[str, Any]:
    # Placeholder: En S1 simplemente enviamos a generación directa para simular
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
    
    prompt = gatekeeper_prompt.format(
        user_message=user_message,
        context="No context applied yet", # Placeholder para S1
        generated_response=last_ai_message
    )
    
    response_text = await llm_service.generate([HumanMessage(content=prompt)])
    decision = response_text.strip().upper()
    
    if "REJECT" in decision and state.get("retry_count", 0) < 3:
        logger.warning(f"Gatekeeper rechazó la respuesta. Reintentando ({state.get('retry_count', 0) + 1}/3)")
        # Quitar el mensaje rechazado
        return {"messages": [], "retry_count": state.get("retry_count", 0) + 1, "current_node": "direct_generate_node"}
        
    logger.info("Gatekeeper aprobó la respuesta.")
    return {"current_node": "end"}
