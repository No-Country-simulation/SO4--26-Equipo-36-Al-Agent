"""
Incluye el endpoint /health para verificar el estado del sistema
y la conectividad con PostgreSQL.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.agent import router as agent_router

router = APIRouter()

router.include_router(agent_router, prefix="/agent")


@router.get("/health", tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Verifica el estado de la aplicación y la conectividad con la DB.

    Returns:
        200 OK con el status del sistema y la base de datos.
    """
    db_status = "unhealthy"
    db_detail = ""

    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_status = "healthy"
            db_detail = "PostgreSQL connected"
    except Exception as e:
        db_detail = str(e)

    status = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": status,
        "service": "ConversaAI API",
        "version": "0.1.0",
        "database": {
            "status": db_status,
            "detail": db_detail,
        },
    }
