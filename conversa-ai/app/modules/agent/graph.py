"""
Definición del StateGraph de LangGraph para el Agente Conversacional.
Implementa un grafo cíclico con nodos para:
  - Routing (Supervisor)
  - RAG (Hybrid Search + Generate)
  - SQL (Tool Executor)
  - Step-Up Auth (OTP)
  - Greeting / Out-of-Scope
  - Gatekeeper (Auditor)
  - Memory (Episodic Update)
"""

from langgraph.graph import StateGraph, START, END

from app.modules.agent.schemas import AgentState
from app.modules.agent.nodes import (
    supervisor_node,
    greeting_node,
    out_of_scope_node,
    rag_node,
    rag_generate_node,
    sql_node,
    step_up_auth_node,
    gatekeeper_node,
    update_memory_node,
)

# Inicializar el StateGraph con nuestro TypedDict
workflow = StateGraph(AgentState)

# ── Registrar nodos ──
workflow.add_node("supervisor_node", supervisor_node)
workflow.add_node("greeting_node", greeting_node)
workflow.add_node("out_of_scope_node", out_of_scope_node)
workflow.add_node("rag_node", rag_node)
workflow.add_node("rag_generate_node", rag_generate_node)
workflow.add_node("sql_node", sql_node)
workflow.add_node("step_up_auth_node", step_up_auth_node)
workflow.add_node("gatekeeper_node", gatekeeper_node)
workflow.add_node("update_memory_node", update_memory_node)

# ── START → Supervisor ──
workflow.add_edge(START, "supervisor_node")


# ── Aristas condicionales desde el Supervisor ──
def route_from_supervisor(state: AgentState) -> str:
    """Retorna el nombre del nodo al que rutea el supervisor."""
    target = state["current_node"]
    # Si la intención es SQL y no está autenticado, redirigir a step-up auth
    if target == "sql_node" and not state.get("is_authenticated", False):
        return "step_up_auth_node"
    return target


workflow.add_conditional_edges(
    "supervisor_node",
    route_from_supervisor,
    {
        "rag_node": "rag_node",
        "sql_node": "sql_node",
        "step_up_auth_node": "step_up_auth_node",
        "greeting_node": "greeting_node",
        "out_of_scope_node": "out_of_scope_node",
    }
)

# ── Flujo RAG: rag_node → rag_generate_node → gatekeeper_node ──
workflow.add_edge("rag_node", "rag_generate_node")
workflow.add_edge("rag_generate_node", "gatekeeper_node")

# ── Flujo Greeting/OutOfScope: directo a update_memory ──
workflow.add_edge("greeting_node", "update_memory_node")
workflow.add_edge("out_of_scope_node", "update_memory_node")

# ── Flujo SQL: sql_node → update_memory ──
workflow.add_edge("sql_node", "update_memory_node")


# ── Flujo Auth: step_up_auth → condicional ──
def route_from_auth(state: AgentState) -> str:
    """Decide si continuar a SQL (auth exitosa) o terminar (esperando OTP)."""
    return state["current_node"]


workflow.add_conditional_edges(
    "step_up_auth_node",
    route_from_auth,
    {
        "sql_node": "sql_node",
        "end": "update_memory_node",
    }
)


# ── Gatekeeper → condicional (aprobar o re-generar) ──
def route_from_gatekeeper(state: AgentState) -> str:
    """Decide si termina o si necesita regenerar la respuesta."""
    target = state["current_node"]
    if target in ("end", "update_memory_node"):
        return "update_memory_node"
    return target


workflow.add_conditional_edges(
    "gatekeeper_node",
    route_from_gatekeeper,
    {
        "rag_generate_node": "rag_generate_node",
        "greeting_node": "greeting_node",
        "update_memory_node": "update_memory_node",
    }
)

# ── Nodo final siempre termina ──
workflow.add_edge("update_memory_node", END)

# ── Compilar el grafo ──
agent_app = workflow.compile()
