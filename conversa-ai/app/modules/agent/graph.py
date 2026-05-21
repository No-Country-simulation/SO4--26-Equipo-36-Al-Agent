from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.modules.agent.schemas import AgentState
from app.modules.agent.nodes import (
    supervisor_node,
    direct_generate_node,
    rag_node,
    rag_generate_node,
    sql_node,
    gatekeeper_node
)

# Inicializar el StateGraph con nuestro TypedDict
workflow = StateGraph(AgentState)

# Añadir los nodos al grafo
workflow.add_node("supervisor_node", supervisor_node)
workflow.add_node("direct_generate_node", direct_generate_node)
workflow.add_node("rag_node", rag_node)
workflow.add_node("rag_generate_node", rag_generate_node)
workflow.add_node("sql_node", sql_node)
workflow.add_node("gatekeeper_node", gatekeeper_node)

# Flujo: START -> Supervisor
workflow.add_edge(START, "supervisor_node")

# Aristas condicionales desde el Supervisor
def route_from_supervisor(state: AgentState) -> str:
    """Retorna el nombre del nodo al que rutea el supervisor."""
    return state["current_node"]

workflow.add_conditional_edges(
    "supervisor_node",
    route_from_supervisor,
    {
        "rag_node": "rag_node",
        "sql_node": "sql_node",
        "direct_generate_node": "direct_generate_node",
    }
)

# Flujos de RAG
workflow.add_edge("rag_node", "rag_generate_node")
workflow.add_edge("rag_generate_node", "gatekeeper_node")

# Otros flujos (SQL fluye a direct por ahora)
workflow.add_edge("sql_node", "direct_generate_node")
workflow.add_edge("direct_generate_node", "gatekeeper_node")

# Aristas condicionales desde el Gatekeeper
def route_from_gatekeeper(state: AgentState) -> str:
    """Decide si termina o si necesita regenerar."""
    if state["current_node"] == "end":
        return END
    return state["current_node"]

workflow.add_conditional_edges(
    "gatekeeper_node",
    route_from_gatekeeper,
    {
        "direct_generate_node": "direct_generate_node",
        "rag_generate_node": "rag_generate_node",
        END: END
    }
)

# Compilar el grafo
agent_app = workflow.compile()
