"""
Endpoints del evaluador: gatillar pipeline ETL y consultar estado.

POST /api/v1/evaluator/run-pipeline  → 202 Accepted + run_id
GET  /api/v1/evaluator/status/{id}   → estado de la ejecución
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.logging import get_logger
from app.modules.evaluator.etl import run_pipeline, get_pipeline_status

logger = get_logger("api.evaluator")

router = APIRouter(tags=["Evaluator"])


@router.post("/run-pipeline", status_code=202)
async def trigger_pipeline(background_tasks: BackgroundTasks) -> dict:
    """Gatilla el pipeline ETL del evaluador como tarea de fondo.

    No bloquea el módulo agente (BackgroundTasks).
    Requiere permiso: pipeline:execute (preparado para JWT futuro).
    """
    run_id = str(uuid.uuid4())
    logger.info(f"Pipeline ETL solicitado — run_id={run_id}")

    background_tasks.add_task(run_pipeline, run_id)

    return {
        "message": "Pipeline ETL iniciado en segundo plano",
        "pipeline_run_id": run_id,
        "status": "RUNNING",
    }


@router.get("/status/{run_id}")
async def pipeline_status(run_id: str) -> dict:
    """Consulta el estado de una ejecución del pipeline."""
    result = get_pipeline_status(run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline run no encontrado")

    return result.model_dump(mode="json")
