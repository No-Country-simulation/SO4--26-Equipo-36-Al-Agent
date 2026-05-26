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
    
    # Retornar HTML para HTMX swap
    icon = "👍" if rating == 1 else "👎"
    return HTMLResponse(
        content=f'<span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">{icon} Gracias por tu feedback</span>'
    )


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
        await DBService.save_session_rating(session_id, rating, comment)
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
        await DBService.close_session(session_id)
    except Exception as e:
        logger.error(f"Error cerrando sesión: {e}")
        raise HTTPException(status_code=500, detail="Error al cerrar la sesión")
    
    return {"status": "success", "message": "Sesión cerrada"}


@router.post("/close-session-form", tags=["Agent"])
async def close_session_form(
    request: Request,
    session_id: str = Form(...),
):
    """
    Cierra la sesión y retorna el widget HTMX de calificación.
    """
    logger.info(f"Cerrando sesión vía UI: {session_id}")
    
    from app.modules.agent.db_service import DBService
    try:
        await DBService.close_session(session_id)
    except Exception as e:
        logger.error(f"Error cerrando sesión: {e}")
        # Retornamos de todas formas el widget aunque falle el DB update
    
    return templates.TemplateResponse(
        request=request,
        name="components/session_rating_widget.html",
        context={"session_id": session_id}
    )
