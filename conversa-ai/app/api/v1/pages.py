"""
API de renderizado de páginas (SSR) y gestión de WebSockets.
Gestiona la comunicación bidireccional en tiempo real del chat.
"""

import uuid
import json
import asyncio
import re
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage, AIMessage

from app.modules.agent.graph import agent_app
from app.modules.agent.db_service import DBService
from app.modules.agent.memory_service import MemoryService
from app.core.logging import get_logger

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = get_logger(__name__)

# Diccionario en memoria para el historial de sesiones
session_store: dict = {}
# Estado de autenticación por sesión
auth_store: dict = {}


def sanitize_for_html(text: str) -> str:
    """
    Convierte markdown crudo a texto limpio para presentación en el chat.
    Elimina: **, ##, *, _, `, viñetas markdown.
    Convierte saltos de línea a <br>.
    """
    # Eliminar headers markdown
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Eliminar bold/italic
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Convertir viñetas markdown a bullet Unicode
    text = re.sub(r'^\s*[-*+]\s+', '• ', text, flags=re.MULTILINE)
    # Eliminar backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Limpiar líneas vacías excesivas
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Convertir newlines a <br> para HTML
    text = text.replace('\n', '<br>')
    return text.strip()


@router.get("/")
async def landing(request: Request):
    """Renderiza la landing page con un session_id único."""
    return templates.TemplateResponse(
        request=request,
        name="pages/landing.html",
        context={"session_id": str(uuid.uuid4())}
    )


@router.get("/chat")
async def chat_full(request: Request):
    """Renderiza la vista de chat a pantalla completa."""
    return templates.TemplateResponse(
        request=request,
        name="pages/chat_full.html",
        context={"session_id": str(uuid.uuid4())}
    )


@router.websocket("/api/v1/pages/ws/{client_session_id}")
async def websocket_endpoint(websocket: WebSocket, client_session_id: str):
    """
    Endpoint WebSocket principal del chat.
    Gestiona el ciclo de vida completo de la conversación:
    - Recepción de mensajes del usuario
    - Typing indicator
    - Ejecución del StateGraph de LangGraph
    - Streaming typewriter de la respuesta
    - Feedback y timeout de sesión
    """
    await websocket.accept()

    # Obtener IDs reales de la base de datos
    user_id, session_id = await DBService.get_or_create_user_and_session(client_session_id)

    if session_id not in session_store:
        session_store[session_id] = []

    # Auth state: por defecto NO autenticado (el usuario debe verificar con OTP)
    is_authenticated = auth_store.get(session_id, False)

    logger.info(
        f"WebSocket conectado: session={session_id}, user={user_id}",
        extra={"session_id": session_id, "user_id": user_id}
    )

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_message = payload.get("user_message", "").strip()
                if not user_message:
                    continue
            except json.JSONDecodeError:
                user_message = data.strip()
                if not user_message:
                    continue

            # Guardar mensaje del usuario en DB
            await DBService.save_message(session_id, role_id=1, content=user_message)

            # Render user message bubble
            user_html = templates.get_template("components/msg_text.html").render({
                "role": "user",
                "content": user_message
            })
            await websocket.send_text(user_html)

            # Send typing indicator
            typing_html = templates.get_template("components/msg_typing.html").render({})
            await websocket.send_text(typing_html)

            # Agregar al historial en memoria
            session_store[session_id].append(HumanMessage(content=user_message))

            # Recuperar memorias relevantes del usuario para enriquecer el contexto
            user_memories = ""
            try:
                user_memories = await MemoryService.retrieve_relevant_memories(
                    user_id=user_id,
                    query=user_message,
                    top_k=3
                )
            except Exception as e:
                logger.warning(f"Error recuperando memorias: {e}")

            # Preparar estado para LangGraph
            state = {
                "messages": session_store[session_id].copy(),
                "user_id": user_id,
                "session_id": session_id,
                "channel_id": 1,
                "current_node": "supervisor_node",
                "retry_count": 0,
                "is_authenticated": is_authenticated,
                "context": "",
                "user_email": None,
                "user_phone": None,
                "user_full_name": None,
                "otp_pending": False,
                "last_activity_at": None,
                "session_rating": None,
                "user_memories": user_memories,
            }

            # Crear ID único para este bubble de respuesta
            msg_id = str(uuid.uuid4())

            # Ejecutar el grafo
            try:
                final_state = await agent_app.ainvoke(state)
            except Exception as e:
                logger.error(f"Error ejecutando el grafo: {e}", extra={
                    "session_id": session_id, "user_id": user_id
                })
                final_state = {"messages": []}

            # Actualizar estado de autenticación persistente por sesión
            if final_state.get("is_authenticated"):
                is_authenticated = True
                auth_store[session_id] = True

            final_messages = final_state.get("messages", [])

            # Extraer la última respuesta del asistente
            final_content = "Lo siento, ocurrió un error al procesar tu solicitud. Por favor, intentá de nuevo."
            if final_messages:
                last_msg = final_messages[-1]
                if isinstance(last_msg, AIMessage):
                    session_store[session_id].append(last_msg)
                    final_content = last_msg.content

            # Sanitizar markdown para presentación HTML limpia
            final_content_html = sanitize_for_html(final_content)

            # Enviar bubble vacío del asistente reemplazando al typing indicator
            initial_assistant_html = templates.get_template("components/msg_text.html").render({
                "role": "assistant",
                "content": "",
                "msg_id": msg_id,
                "swap_target": "outerHTML:#typing-indicator"
            })
            await websocket.send_text(initial_assistant_html)

            # Efecto Typewriter (streaming artificial)
            chunk_size = 4
            for i in range(0, len(final_content_html), chunk_size):
                chunk = final_content_html[i:i + chunk_size]
                stream_html = f'<span hx-swap-oob="beforeend:#response-{msg_id}">{chunk}</span>'
                await websocket.send_text(stream_html)
                await asyncio.sleep(0.012)

            # Remover quick replies si existen (después del primer mensaje)
            remove_quick = '<div id="quick-replies" hx-swap-oob="outerHTML"></div>'
            await websocket.send_text(remove_quick)

            # Si la sesión finalizó semánticamente, enviar widget de rating
            if final_state.get("is_finished"):
                rating_html = templates.get_template("components/session_rating_widget.html").render({"session_id": session_id})
                await websocket.send_text(rating_html)

    except WebSocketDisconnect:
        logger.info(
            f"WebSocket desconectado: session={session_id}",
            extra={"session_id": session_id, "user_id": user_id}
        )
    except Exception as e:
        logger.error(
            f"Error inesperado en WebSocket: {e}",
            extra={"session_id": session_id, "user_id": user_id}
        )
