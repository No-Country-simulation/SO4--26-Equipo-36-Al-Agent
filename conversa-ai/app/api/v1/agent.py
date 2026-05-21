from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/feedback", tags=["Agent"])
async def submit_feedback(
    message_id: str = Body(...),
    rating: int = Body(..., description="1 para pulgar arriba, -1 para pulgar abajo"),
    db: AsyncSession = Depends(get_db)
):
    """
    Recibe la calificación de una respuesta del agente (👍/👎).
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
    
    return {"status": "success", "message": "Feedback registrado correctamente"}
