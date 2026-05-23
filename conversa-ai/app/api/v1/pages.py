import uuid
import json
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage

from app.modules.agent.graph import agent_app

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("pages/landing.html", {"request": request, "session_id": str(uuid.uuid4())})

@router.get("/chat")
async def chat_full(request: Request):
    return templates.TemplateResponse("pages/chat_full.html", {"request": request, "session_id": str(uuid.uuid4())})

@router.websocket("/api/v1/pages/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
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
            
            # Prepare state for LangGraph
            state = {
                "messages": [HumanMessage(content=user_message)],
                "user_id": "demo_user",
                "session_id": session_id,
                "channel_id": 1,
                "current_node": "supervisor_node",
                "retry_count": 0,
                "is_authenticated": False,
                "context": ""
            }
            
            # Create a unique ID for this response bubble
            msg_id = str(uuid.uuid4())
            
            # Remove typing indicator by sending an empty div with oob
            remove_typing = '<div id="typing-indicator" hx-swap-oob="outerHTML"></div>'
            await websocket.send_text(remove_typing)
            
            # Send initial empty assistant bubble
            initial_assistant_html = templates.get_template("components/msg_text.html").render({
                "role": "assistant",
                "content": "",
                "msg_id": msg_id
            })
            await websocket.send_text(initial_assistant_html)
            
            # Streaming from LangGraph
            final_content = ""
            async for event in agent_app.astream_events(state, version="v1"):
                kind = event["event"]
                # Capture model streaming
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        # Append the chunk string directly via HTMX OOB to the bubble
                        # Replace newlines with <br> for HTML rendering
                        safe_chunk = chunk.replace("\n", "<br>").replace("\r", "")
                        stream_html = f'<span hx-swap-oob="beforeend:#response-{msg_id}">{safe_chunk}</span>'
                        await websocket.send_text(stream_html)
                        final_content += chunk

            # Si el agente no retornó nada por streaming, mandar un placeholder de fallo
            if not final_content:
                error_html = f'<span hx-swap-oob="beforeend:#response-{msg_id}">Lo siento, ha ocurrido un error al procesar tu solicitud.</span>'
                await websocket.send_text(error_html)
                
    except WebSocketDisconnect:
        pass
