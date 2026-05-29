"""
Modelos Pydantic intermedios para cada etapa del pipeline ETL.

ExtractedSession → CleanedSession → ClassifiedSession → ResolvedSession
                                                          ↓
                                                   PipelineResult
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Enums

class SentimentLabel(str, Enum):
    POS = "POS"
    NEG = "NEG"
    NEU = "NEU"


class ResolutionType(str, Enum):
    SUCCESS = "SUCCESS"
    FRUSTRATION = "FRUSTRATION"
    NEUTRAL = "NEUTRAL"


# Etapa 1: Extract

class ExtractedMessage(BaseModel):
    """Mensaje individual extraído del OLTP."""
    message_id: UUID
    role: str
    content: str
    created_at: datetime


class ExtractedSession(BaseModel):
    """Sesión completa extraída de agent_core con todos sus datos asociados."""
    session_id: UUID
    user_id: UUID
    language_iso: str = "es"
    start_time: datetime
    end_time: Optional[datetime] = None
    retry_count: int = 0
    messages: list[ExtractedMessage] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    positive_feedback_count: int = 0
    negative_feedback_count: int = 0
    star_rating: Optional[int] = None
    is_authenticated: bool = False


# Etapa 2: Transform (Clean)

class CleanedSession(ExtractedSession):
    """Sesión con texto limpio (PII removida) y texto de usuario concatenado."""
    user_text_concat: str = ""
    total_messages: int = 0


# Etapa 3: Classify

class ClassifiedSession(CleanedSession):
    """Sesión con clasificación de sentimiento (pysentimiento)."""
    sentiment_label: SentimentLabel = SentimentLabel.NEU
    sentiment_score: float = 0.0
    intent_name: str = "intent_desconocido"
    intent_category: str = "general"


# Etapa 4: Resolve

class ResolvedSession(ClassifiedSession):
    """Sesión con resolución final y métricas consolidadas para el warehouse."""
    resolution: ResolutionType = ResolutionType.NEUTRAL
    is_abandoned: bool = False
    session_duration_seconds: int = 0
    auto_tags: list[str] = Field(default_factory=list)


# Resultado del Pipeline

class PipelineResult(BaseModel):
    """Resumen de la ejecución completa del pipeline ETL."""
    pipeline_run_id: str
    status: str = "RUNNING"
    total_sessions: int = 0
    processed: int = 0
    errors: int = 0
    skipped: int = 0
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_details: list[str] = Field(default_factory=list)
