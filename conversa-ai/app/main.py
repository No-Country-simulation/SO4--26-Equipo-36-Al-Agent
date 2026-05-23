"""
Configura CORS, lifespan events (inicio/cierre de DB), e incluye
el router principal de la API v1.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import router as api_v1_router
from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación.

    - Startup: verifica conectividad con la DB.
    - Shutdown: cierra el pool de conexiones.
    """
    # Startup
    async with engine.begin() as conn:
        await conn.execute(
            __import__("sqlalchemy").text("SELECT 1")
        )
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description=(
        "Sistema de Observabilidad y Análisis de Conversaciones entre el agente y los clientes. "
        "Ecosistema dual: Agente Conversacional + Evaluador Analítico."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
from app.api.v1.pages import router as pages_router
app.include_router(pages_router)
app.include_router(api_v1_router, prefix="/api/v1")
