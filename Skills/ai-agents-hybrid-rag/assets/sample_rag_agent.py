"""
Skills/ai-agents-hybrid-rag/assets/langgraph_rag_flow.py

Ejemplo de referencia industrial: Implementación de un grafo conversacional
con LangGraph, inyección de RAG, ruteo híbrido y validación por auditor (Gatekeeper).
"""

from typing import Dict, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END


# 1. Definición del Estado del Grafo (State)
class AgentState(TypedDict):
    messages: list[BaseMessage]
    context: str
    query_type: Literal["transactional", "informational", "general"]
    is_hallucination: bool
    retry_count: int


# 2. Nodo de Ruteo Inicial (Router)
def intent_router(state: AgentState) -> Dict[str, str]:
    """Determina si la consulta es transaccional (SQL) o informativa (RAG)."""
    last_message = state["messages"][-1].content.lower()
    
    # Ruteo determinista / semántico
    if any(keyword in last_message for keyword in ["saldo", "transaccion", "tarjeta", "cuenta"]):
        return "transactional"
    elif any(keyword in last_message for keyword in ["como", "que es", "requisito", "politica"]):
        return "informational"
    return "general"


# 3. Nodos de Acción
def retrieve_vector_db(state: AgentState) -> Dict[str, any]:
    """Nodo RAG: Simula recuperación semántica estructurada (ChromaDB)."""
    query = state["messages"][-1].content
    print(f"[RAG Node] Ejecutando búsqueda semántica para: '{query}'")
    
    # Simulación de fragmento recuperado con estructura preservada
    retrieved_chunk = (
        "POLÍTICA DE TARJETAS (Sección 4.2): Las tarjetas de crédito inactivas durante "
        "más de 90 días se bloquearán automáticamente por motivos de seguridad. "
        "El cliente puede reactivarlas llamando al soporte oficial."
    )
    return {"context": retrieved_chunk}


def query_relational_db(state: AgentState) -> Dict[str, any]:
    """Nodo SQL: Simula ejecución de herramienta determinista en PostgreSQL."""
    print("[SQL Node] Consultando base de datos relacional para datos estructurados...")
    db_result = "Cuenta activa. Saldo disponible: $15,230.50. Última transacción: Ayer."
    return {"context": db_result}


def general_assistant(state: AgentState) -> Dict[str, any]:
    """Nodo de Asistente General: Conversación libre."""
    print("[General Node] Procesando consulta general...")
    return {"context": "No se requiere recuperación adicional."}


def generate_response(state: AgentState) -> Dict[str, any]:
    """Genera la respuesta del LLM basándose estrictamente en el contexto."""
    context = state.get("context", "")
    query = state["messages"][-1].content
    
    print(f"[LLM Node] Generando respuesta con contexto: {context[:60]}...")
    
    # Simulación de respuesta basada 100% en el contexto
    if "saldo" in query.lower():
        response = f"Facu, de acuerdo a tu consulta, tu saldo es de $15,230.50."
    elif "bloquear" in query.lower() or "inactiva" in query.lower():
        response = "Según nuestras políticas, las tarjetas inactivas por más de 90 días se bloquean automáticamente."
    else:
        response = "¡Hola! ¿En qué puedo ayudarte hoy?"
        
    return {"messages": [AIMessage(content=response)]}


# 4. Nodo Auditor / Gatekeeper (Evitación de Alucinaciones)
def gatekeeper_validator(state: AgentState) -> Dict[str, any]:
    """Audita si la respuesta generada alucina o se desvía del contexto."""
    last_response = state["messages"][-1].content
    context = state.get("context", "")
    
    print("[Gatekeeper Node] Auditando fidelidad de la respuesta...")
    
    # En producción, esto se realiza mediante un LLM de bajo costo con prompts estructurados (JSON output)
    # Aquí simulamos la validación lógica
    if "saldo" in last_response.lower() and "15,230.50" not in context:
        print("[WARNING] ¡Alucinación detectada! El saldo no figura en el contexto.")
        return {"is_hallucination": True}
        
    print("[SUCCESS] Respuesta validada correctamente.")
    return {"is_hallucination": False}


# 5. Arista Condicional post-auditoría
def route_after_audit(state: AgentState) -> str:
    if state.get("is_hallucination", False) and state.get("retry_count", 0) < 3:
        return "regenerate"
    return "finalize"


# 6. Construcción y Orquestación del Grafo
def build_orchestrator():
    workflow = StateGraph(AgentState)
    
    # Agregar Nodos
    workflow.add_node("rag_retrieve", retrieve_vector_db)
    workflow.add_node("sql_query", query_relational_db)
    workflow.add_node("general_handler", general_assistant)
    workflow.add_node("generator", generate_response)
    workflow.add_node("gatekeeper", gatekeeper_validator)
    
    # Definir el enrutamiento inicial
    workflow.set_conditional_entry_point(
        intent_router,
        {
            "transactional": "sql_query",
            "informational": "rag_retrieve",
            "general": "general_handler"
        }
    )
    
    # Conexiones de Nodos de Recuperación a Generación
    workflow.add_edge("rag_retrieve", "generator")
    workflow.add_edge("sql_query", "generator")
    workflow.add_edge("general_handler", "generator")
    
    # Generación a Auditoría
    workflow.add_edge("generator", "gatekeeper")
    
    # Enrutamiento basado en la validación del Gatekeeper
    workflow.add_conditional_edges(
        "gatekeeper",
        route_after_audit,
        {
            "regenerate": "generator",  # Intenta re-generar
            "finalize": END            # Termina el flujo de forma segura
        }
    )
    
    return workflow.compile()


if __name__ == "__main__":
    app_graph = build_orchestrator()
    print("Grafo de LangGraph compilado con éxito.")
