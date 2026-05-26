from fastapi import APIRouter, Depends, HTTPException, Body, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.core.database import get_db
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
templates = Jinja2Templates(directory="app/templates")


@router.post("/feedback", tags=["Agent"])
async def submit_feedback(
    request: Request,
    message_id: str = Form(...),
    rating: int = Form(..., description="1 para pulgar arriba, -1 para pulgar abajo"),
):
    """
    Recibe la calificación de una respuesta del agente (👍/👎).
    Retorna HTML para reemplazar los botones de feedback vía HTMX.
    """
    if rating not in [1, -1]:
        raise HTTPException(status_code=400, detail="Rating debe ser 1 o -1")
        
    logger.info(f"Feedback recibido para mensaje {message_id}: {rating}")
    
    from app.modules.agent.db_service import DBService
    try:
        await DBService.save_feedback(message_id, rating)
    except Exception as e:
        logger.error(f"Error guardando feedback: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el feedback")
    
    # Retornar HTML para HTMX swap (botones deshabilitados con el color elegido)
    like_color = "text-green-500" if rating == 1 else "text-gray-600 opacity-50"
    dislike_color = "text-red-500" if rating == -1 else "text-gray-600 opacity-50"
    
    html = f"""
    <button class="p-1 {like_color}" disabled title="Gracias por tu feedback">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
        </svg>
    </button>
    <button class="p-1 {dislike_color}" disabled title="Gracias por tu feedback">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
        </svg>
    </button>
    """
    return HTMLResponse(content=html)


@router.post("/session-rating", tags=["Agent"])
async def submit_session_rating(
    request: Request,
    session_id: str = Form(...),
    rating: int = Form(..., description="Rating de 1 a 5 estrellas"),
    comment: Optional[str] = Form(None),
):
    """
    Recibe el rating de estrellas (1-5) para una sesión finalizada.
    """
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating debe estar entre 1 y 5")
    
    logger.info(f"Session rating recibido: session={session_id}, rating={rating}")
    
    from app.modules.agent.db_service import DBService
    try:
        real_session_id = await DBService.get_real_session_id(session_id)
        if not real_session_id:
            raise ValueError(f"No real session found for {session_id}")
        await DBService.save_session_rating(real_session_id, rating, comment)
    except Exception as e:
        logger.error(f"Error guardando session rating: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el rating")
    
    # Retornar HTML para reemplazar las estrellas
    return HTMLResponse(
        content='<p class="text-brand-lime font-bold text-sm uppercase tracking-widest text-center mt-2">¡Gracias por tu calificación!</p>'
    )


@router.post("/close-session", tags=["Agent"])
async def close_session(
    session_id: str = Form(...),
):
    """
    Cierra una sesión manualmente (marca como FINISHED).
    """
    logger.info(f"Cerrando sesión: {session_id}")
    
    from app.modules.agent.db_service import DBService
    try:
        real_session_id = await DBService.get_real_session_id(session_id)
        if real_session_id:
            await DBService.close_session(real_session_id)
    except Exception as e:
        logger.error(f"Error cerrando sesión: {e}")
        raise HTTPException(status_code=500, detail="Error al cerrar la sesión")
    
    return {"status": "success", "message": "Sesión cerrada"}


@router.post("/close-session-form", tags=["Agent"])
async def close_session_form(
    request: Request,
    session_id: str = Form(...),
    timeout: bool = Form(False),
):
    """
    Cierra la sesión y retorna el widget HTMX de calificación.
    """
    logger.info(f"Cerrando sesión vía UI: {session_id}")
    
    from app.modules.agent.db_service import DBService
    try:
        real_session_id = await DBService.get_real_session_id(session_id)
        if real_session_id:
            await DBService.close_session(real_session_id)
    except Exception as e:
        logger.error(f"Error cerrando sesión: {e}")
        # Retornamos de todas formas el widget aunque falle el DB update
    
    return templates.TemplateResponse(
        request=request,
        name="components/session_rating_widget.html",
        context={"session_id": session_id, "timeout": timeout}
    )
