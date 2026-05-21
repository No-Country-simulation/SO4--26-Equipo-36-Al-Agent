import asyncio
from fastapi import APIRouter, Request, Response, BackgroundTasks, Depends
from fastapi.responses import PlainTextResponse
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.agent.graph import agent_app
from langchain_core.messages import HumanMessage

router = APIRouter()
logger = get_logger(__name__)


async def process_whatsapp_message(payload: Dict[str, Any]):
    """
    Procesa un mensaje entrante de WhatsApp en background.
    """
    try:
        # 1. Extraer datos del payload de Meta
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        messages = value.get("messages", [])
        if not messages:
            return
            
        message = messages[0]
        message_text = message.get("text", {}).get("body", "")
        sender_phone = message.get("from")
        message_id = message.get("id")
        
        # Como no tenemos un session_id explícito desde WhatsApp en este MVP inicial,
        # usaremos el número de teléfono como user_id y session_id por ahora.
        user_id = f"wa_{sender_phone}"
        session_id = f"sess_{sender_phone}"
        
        # En el MVP, inicializamos el state manualmente con LangGraph
        state = {
            "messages": [HumanMessage(content=message_text)],
            "user_id": user_id,
            "session_id": session_id,
            "channel_id": 1, # WhatsApp
            "current_node": "supervisor_node",
            "retry_count": 0,
            "is_authenticated": False
        }
        
        # 2. Invocar el grafo del agente
        # agent_app es el grafo compilado en graph.py
        result = await agent_app.ainvoke(state)
        
        # 3. Obtener respuesta y enviar (Simulación de envío)
        final_messages = result.get("messages", [])
        if final_messages:
            final_response = final_messages[-1].content
            logger.info(f"Enviando respuesta a {sender_phone}: {final_response}")
            # Acá iría la llamada a Meta API (whatsapp_service.py) en la siguiente iteración
            
    except Exception as e:
        logger.error(f"Error procesando mensaje de WhatsApp: {str(e)}")


@router.get("/webhook/whatsapp", tags=["Webhooks"])
async def verify_whatsapp_webhook(request: Request):
    """
    Endpoint para verificación inicial de Webhook por parte de Meta.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.VERIFY_TOKEN:
            logger.info("Webhook de WhatsApp verificado exitosamente.")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            logger.warning("Token de verificación de WhatsApp inválido.")
            return Response(status_code=403)
            
    return Response(status_code=400)


@router.post("/webhook/whatsapp", tags=["Webhooks"])
async def receive_whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Recibe notificaciones de mensajes entrantes de WhatsApp.
    Devuelve 202 inmediatamente y procesa el mensaje de fondo.
    """
    try:
        payload = await request.json()
        logger.info("Mensaje de WhatsApp recibido.")
        
        # Delegar procesamiento asíncrono para no bloquear la respuesta
        background_tasks.add_task(process_whatsapp_message, payload)
        
        return Response(status_code=202)
        
    except Exception as e:
        logger.error(f"Error al parsear payload de WhatsApp: {str(e)}")
        return Response(status_code=400)
