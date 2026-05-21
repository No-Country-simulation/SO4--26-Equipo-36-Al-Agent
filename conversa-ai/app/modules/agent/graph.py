from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.modules.agent.schemas import AgentState
from app.modules.agent.nodes import (
    supervisor_node,
    direct_generate_node,
    rag_node,
    rag_generate_node,
    sql_node,
    step_up_auth_node,
    gatekeeper_node,
    update_memory_node
)

# Inicializar el StateGraph con nuestro TypedDict
workflow = StateGraph(AgentState)

# Añadir los nodos al grafo
workflow.add_node("supervisor_node", supervisor_node)
workflow.add_node("direct_generate_node", direct_generate_node)
workflow.add_node("rag_node", rag_node)
workflow.add_node("rag_generate_node", rag_generate_node)
workflow.add_node("sql_node", sql_node)
workflow.add_node("step_up_auth_node", step_up_auth_node)
workflow.add_node("gatekeeper_node", gatekeeper_node)
workflow.add_node("update_memory_node", update_memory_node)

# Flujo: START -> Supervisor
workflow.add_edge(START, "supervisor_node")

# Aristas condicionales desde el Supervisor
def route_from_supervisor(state: AgentState) -> str:
    """Retorna el nombre del nodo al que rutea el supervisor."""
    # Si la intención es SQL y no está autenticado, vamos a step-up auth
    if state["current_node"] == "sql_node" and not state.get("is_authenticated", False):
        return "step_up_auth_node"
    return state["current_node"]

workflow.add_conditional_edges(
    "supervisor_node",
    route_from_supervisor,
    {
        "rag_node": "rag_node",
        "sql_node": "sql_node",
        "step_up_auth_node": "step_up_auth_node",
        "direct_generate_node": "direct_generate_node",
    }
)

# Flujos de RAG
workflow.add_edge("rag_node", "rag_generate_node")
workflow.add_edge("rag_generate_node", "gatekeeper_node")

# Flujos de SQL y Auth
def route_from_auth(state: AgentState) -> str:
    return state["current_node"]

workflow.add_conditional_edges(
    "step_up_auth_node",
    route_from_auth,
    {
        "sql_node": "sql_node",
        "end": "update_memory_node"
    }
)

workflow.add_edge("sql_node", "update_memory_node") # Al finalizar la transaccion, extrae memoria

# Otros flujos
workflow.add_edge("direct_generate_node", "gatekeeper_node")

# Aristas condicionales desde el Gatekeeper
def route_from_gatekeeper(state: AgentState) -> str:
    """Decide si termina o si necesita regenerar."""
    if state["current_node"] == "end":
        return "update_memory_node"
    if state["current_node"] == "update_memory_node":
        return "update_memory_node"
    return state["current_node"]

workflow.add_conditional_edges(
    "gatekeeper_node",
    route_from_gatekeeper,
    {
        "direct_generate_node": "direct_generate_node",
        "rag_generate_node": "rag_generate_node",
        "update_memory_node": "update_memory_node",
        END: END
    }
)

# El último nodo siempre termina
workflow.add_edge("update_memory_node", END)

# Compilar el grafo
agent_app = workflow.compile()
