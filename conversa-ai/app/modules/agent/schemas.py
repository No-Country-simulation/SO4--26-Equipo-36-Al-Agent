from typing import List, Optional, TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Estado inmutable (StateGraph) del Agente Conversacional.
    Almacena el contexto de la conversación, datos de la sesión y metadatos de control.
    """
    messages: List[BaseMessage]
    user_id: str
    session_id: str
    channel_id: Optional[int]
    
    # Variables de control de flujo
    current_node: str
    retry_count: int
    is_authenticated: bool
