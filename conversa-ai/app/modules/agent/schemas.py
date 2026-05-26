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
    is_finished: bool
    context: Optional[str]

    # Auth / OTP
    user_email: Optional[str]
    user_phone: Optional[str]
    user_full_name: Optional[str]
    otp_pending: bool

    # Session management
    last_activity_at: Optional[str]
    session_rating: Optional[int]

    # Memory context
    user_memories: Optional[str]
