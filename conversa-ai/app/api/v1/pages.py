import uuid
import json
import asyncio
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage, AIMessage

from app.modules.agent.graph import agent_app

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Diccionario en memoria para el historial de sesiones
session_store = {}

@router.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("pages/landing.html", {"request": request, "session_id": str(uuid.uuid4())})

@router.get("/chat")
async def chat_full(request: Request):
    return templates.TemplateResponse("pages/chat_full.html", {"request": request, "session_id": str(uuid.uuid4())})

@router.websocket("/api/v1/pages/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in session_store:
        session_store[session_id] = []
        
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_message = payload.get("user_message", "")
                if not user_message:
                    continue
            except:
                user_message = data
                
            # Render user message
            user_html = templates.get_template("components/msg_text.html").render({"role": "user", "content": user_message})
            await websocket.send_text(user_html)
            
            # Send typing indicator
            typing_html = templates.get_template("components/msg_typing.html").render({})
            await websocket.send_text(typing_html)
            
            # Agregar a historial
            session_store[session_id].append(HumanMessage(content=user_message))
            
            # Usar el UUID de la DB de mock
            user_id = "00000000-0000-0000-0000-000000000001"
            
            # Prepare state for LangGraph
            state = {
                "messages": session_store[session_id].copy(),
                "user_id": user_id,
                "session_id": session_id,
                "channel_id": 1,
                "current_node": "supervisor_node",
                "retry_count": 0,
                "is_authenticated": True, # Forzamos auth para el MVP (o False si queremos testear step-up)
                "context": ""
            }
            
            # Create a unique ID for this response bubble
            msg_id = str(uuid.uuid4())
            
            # Ejecutar el grafo
            final_state = await agent_app.ainvoke(state)
            final_messages = final_state.get("messages", [])
            
            # Actualizar el historial con la última respuesta
            if final_messages:
                last_msg = final_messages[-1]
                if isinstance(last_msg, AIMessage):
                    session_store[session_id].append(last_msg)
                    final_content = last_msg.content
                else:
                    final_content = "Lo siento, ha ocurrido un error al procesar tu solicitud."
            else:
                final_content = "Lo siento, ha ocurrido un error al procesar tu solicitud."
            
            # Remove typing indicator
            remove_typing = '<div id="typing-indicator" hx-swap-oob="outerHTML"></div>'
            await websocket.send_text(remove_typing)
            
            # Send initial empty assistant bubble
            initial_assistant_html = templates.get_template("components/msg_text.html").render({
                "role": "assistant",
                "content": "",
                "msg_id": msg_id
            })
            await websocket.send_text(initial_assistant_html)
            
            # Simular efecto Typewriter (Streaming artificial)
            chunk_size = 3
            for i in range(0, len(final_content), chunk_size):
                chunk = final_content[i:i+chunk_size]
                safe_chunk = chunk.replace("\n", "<br>")
                stream_html = f'<span hx-swap-oob="beforeend:#response-{msg_id}">{safe_chunk}</span>'
                await websocket.send_text(stream_html)
                await asyncio.sleep(0.015) # Retardo para efecto visual neo-brutalista
                
    except WebSocketDisconnect:
        pass
