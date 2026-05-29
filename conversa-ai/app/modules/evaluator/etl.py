"""
Pipeline ETL principal del módulo evaluador.

Flujo: Extract → Transform (PII Clean) → Classify (Sentiment) → Resolve → Load
Ejecutado como BackgroundTask de FastAPI para no bloquear el agente.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.logging import get_logger
from app.modules.evaluator.classifier import sentiment_classifier, intent_extractor
from app.modules.evaluator.schemas import (
    ClassifiedSession,
    CleanedSession,
    ExtractedMessage,
    ExtractedSession,
    PipelineResult,
    ResolutionType,
    ResolvedSession,
    SentimentLabel,
)

logger = get_logger("evaluator.etl")

# ── Almacenamiento en memoria del estado del pipeline ─────────────────────
_pipeline_runs: dict[str, PipelineResult] = {}


def get_pipeline_status(run_id: str) -> Optional[PipelineResult]:
    """Consulta el estado de una ejecución del pipeline."""
    return _pipeline_runs.get(run_id)


# ── Regex para PII Scrubbing ──────────────────────────────────────────────
_PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL]"),
    (re.compile(r"\b\d{2,4}[-.\s]?\d{4}[-.\s]?\d{4}\b"), "[PHONE]"),
    (re.compile(r"\b\d{7,8}\b"), "[DNI]"),
    (re.compile(r"\b\d{2}-?\d{8}-?\d{1}\b"), "[CUIT]"),
    (re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[CARD]"),
    (re.compile(r"https?://\S+", re.IGNORECASE), "[URL]"),
]


# ══════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════

async def run_pipeline(run_id: Optional[str] = None) -> PipelineResult:
    """Orquesta el pipeline ETL completo como tarea de fondo.

    1. EXTRACT — sesiones con status FINISHED (2)
    2. TRANSFORM — PII scrubbing + normalización
    3. CLASSIFY — Sentimiento (HF) + Intent (Groq fallback)
    4. RESOLVE — Heurística tripartita RF#10/RF#11
    5. LOAD — Upsert dims + Insert facts al warehouse
    """
    run_id = run_id or str(uuid.uuid4())
    result = PipelineResult(
        pipeline_run_id=run_id,
        status="RUNNING",
        started_at=datetime.now(timezone.utc),
    )
    _pipeline_runs[run_id] = result

    logger.info(f"Pipeline ETL iniciado — run_id={run_id}")

    try:
        async with async_session_maker() as db:
            # 1. EXTRACT
            sessions = await _extract(db)
            result.total_sessions = len(sessions)
            logger.info(f"Extraídas {len(sessions)} sesiones para procesar")

            if not sessions:
                result.status = "COMPLETED"
                result.finished_at = datetime.now(timezone.utc)
                result.duration_seconds = (
                    result.finished_at - result.started_at
                ).total_seconds()
                return result

            # Marcar como EVALUATING (3)
            await _mark_evaluating(db, [s.session_id for s in sessions])

            # 2. TRANSFORM
            cleaned = [_transform(s) for s in sessions]

            # 3. CLASSIFY
            classified = await _classify(cleaned)

            # 4. RESOLVE
            resolved = [_resolve(s) for s in classified]

            # 5. LOAD
            loaded = await _load(db, resolved)
            result.processed = loaded
            result.errors = len(sessions) - loaded

            result.status = "COMPLETED"

    except Exception as e:
        logger.error(f"Pipeline ETL falló: {e}", exc_info=True)
        result.status = "FAILED"
        result.error_details.append(str(e))
    finally:
        result.finished_at = datetime.now(timezone.utc)
        if result.started_at:
            result.duration_seconds = (
                result.finished_at - result.started_at
            ).total_seconds()
        _pipeline_runs[run_id] = result
        logger.info(
            f"Pipeline ETL finalizado — status={result.status}, "
            f"procesadas={result.processed}/{result.total_sessions}, "
            f"duración={result.duration_seconds:.1f}s"
        )

    return result


# ══════════════════════════════════════════════════════════════════════════
# ETAPA 1: EXTRACT
# ══════════════════════════════════════════════════════════════════════════

async def _extract(db: AsyncSession) -> list[ExtractedSession]:
    """Extrae sesiones FINISHED (status=2) del OLTP con datos asociados."""

    # Query sesiones finalizadas
    sessions_result = await db.execute(text("""
        SELECT s.session_id, s.user_id, s.start_time, s.end_time, s.retry_count,
               COALESCE(cl.iso_code, 'es') AS language_iso,
               CASE WHEN u.email IS NOT NULL AND u.email != '' THEN true ELSE false END AS is_authenticated
        FROM agent_core.sessions s
        LEFT JOIN agent_core.cat_languages cl ON s.language_id = cl.language_id
        LEFT JOIN agent_core.users u ON s.user_id = u.user_id
        WHERE s.status_id = 2
        ORDER BY s.start_time
        LIMIT :batch_size
    """), {"batch_size": settings.EVALUATOR_BATCH_SIZE * 10})

    rows = sessions_result.fetchall()
    if not rows:
        return []

    extracted: list[ExtractedSession] = []

    for row in rows:
        sid = row.session_id

        # Mensajes de la sesión
        msgs_result = await db.execute(text("""
            SELECT m.message_id, cr.role_name, m.content, m.created_at
            FROM agent_core.messages m
            JOIN agent_core.cat_roles cr ON m.role_id = cr.role_id
            WHERE m.session_id = :sid
            ORDER BY m.created_at
        """), {"sid": sid})

        messages = [
            ExtractedMessage(
                message_id=m.message_id,
                role=m.role_name,
                content=m.content,
                created_at=m.created_at,
            )
            for m in msgs_result.fetchall()
        ]

        # Si la sesión no tiene mensajes, no la enviamos al warehouse.
        # La marcamos como evaluada para que el ETL no la vuelva a agarrar.
        if not messages:
            await db.execute(
                text("UPDATE agent_core.sessions SET status_id = 4 WHERE session_id = :sid"),
                {"sid": sid}
            )
            await db.commit()
            continue

        # Tags de la sesión
        tags_result = await db.execute(text("""
            SELECT ct.tag_name
            FROM agent_core.session_tags st
            JOIN agent_core.cat_tags ct ON st.tag_id = ct.tag_id
            WHERE st.session_id = :sid
        """), {"sid": sid})
        tags = [t.tag_name for t in tags_result.fetchall()]

        # Feedback (likes/dislikes por mensaje)
        fb_result = await db.execute(text("""
            SELECT COALESCE(SUM(CASE WHEN f.rating = 1 THEN 1 ELSE 0 END), 0) AS pos,
                   COALESCE(SUM(CASE WHEN f.rating = -1 THEN 1 ELSE 0 END), 0) AS neg
            FROM agent_core.feedback f
            JOIN agent_core.messages m ON f.message_id = m.message_id
            WHERE m.session_id = :sid
        """), {"sid": sid})
        fb = fb_result.fetchone()

        # Star rating
        rating_result = await db.execute(text("""
            SELECT rating FROM agent_core.session_ratings
            WHERE session_id = :sid
            ORDER BY created_at DESC LIMIT 1
        """), {"sid": sid})
        star = rating_result.scalar()

        extracted.append(ExtractedSession(
            session_id=sid,
            user_id=row.user_id,
            language_iso=row.language_iso,
            start_time=row.start_time,
            end_time=row.end_time,
            retry_count=row.retry_count,
            messages=messages,
            tags=tags,
            positive_feedback_count=fb.pos if fb else 0,
            negative_feedback_count=fb.neg if fb else 0,
            star_rating=star,
            is_authenticated=row.is_authenticated,
        ))

    return extracted


async def _mark_evaluating(db: AsyncSession, session_ids: list[uuid.UUID]) -> None:
    """Marca sesiones como EVALUATING (status=3) para evitar reprocesamiento."""
    for sid in session_ids:
        await db.execute(text("""
            UPDATE agent_core.sessions SET status_id = 3
            WHERE session_id = :sid
        """), {"sid": sid})
    await db.commit()


# ══════════════════════════════════════════════════════════════════════════
# ETAPA 2: TRANSFORM (PII Scrubbing)
# ══════════════════════════════════════════════════════════════════════════

def _scrub_pii(text_content: str) -> str:
    """Remueve información personal identificable (PII) del texto."""
    result = text_content
    for pattern, replacement in _PII_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def _transform(session: ExtractedSession) -> CleanedSession:
    """Limpia PII y concatena mensajes del usuario."""
    user_messages: list[str] = []
    cleaned_msgs: list[ExtractedMessage] = []

    for msg in session.messages:
        clean_content = _scrub_pii(msg.content)
        cleaned_msgs.append(ExtractedMessage(
            message_id=msg.message_id,
            role=msg.role,
            content=clean_content,
            created_at=msg.created_at,
        ))
        if msg.role == "user":
            user_messages.append(clean_content)

    return CleanedSession(
        **session.model_dump(exclude={"messages"}),
        messages=cleaned_msgs,
        user_text_concat=" ".join(user_messages),
        total_messages=len(session.messages),
    )


# ══════════════════════════════════════════════════════════════════════════
# ETAPA 3: CLASSIFY (Sentiment + Intent)
# ══════════════════════════════════════════════════════════════════════════

async def _classify(sessions: list[CleanedSession]) -> list[ClassifiedSession]:
    """Clasifica sentimiento (HF) e intent (Groq) para cada sesión."""
    classified: list[ClassifiedSession] = []

    # Batch de sentimiento
    texts_for_sentiment = [
        (s.user_text_concat, s.language_iso) for s in sessions
    ]
    sentiment_results = await sentiment_classifier.classify_batch(texts_for_sentiment)

    for session, sent_result in zip(sessions, sentiment_results):
        # Intent: Extraer usando LLM de Groq (tolerante a rate limits)
        intent_name, intent_category = await intent_extractor.extract_intent(
            session.user_text_concat
        )

        classified.append(ClassifiedSession(
            **session.model_dump(),
            sentiment_label=sent_result.label,
            sentiment_score=sent_result.score,
            intent_name=intent_name,
            intent_category=intent_category,
        ))

    return classified


# ══════════════════════════════════════════════════════════════════════════
# ETAPA 4: RESOLVE (Heurística RF#10/RF#11)
# ══════════════════════════════════════════════════════════════════════════

def _resolve(session: ClassifiedSession) -> ResolvedSession:
    """Aplica la heurística tripartita para determinar la resolución.

    RF#11: Sesiones con <3 msgs y sentimiento neutral → NEUTRAL + is_abandoned
    RF#10: Combina cantidad de mensajes, sentimiento y feedback
    """
    # Calcular duración
    duration = 0
    if session.start_time and session.end_time:
        duration = int((session.end_time - session.start_time).total_seconds())

    auto_tags: list[str] = []
    resolution = ResolutionType.NEUTRAL
    is_abandoned = False

    # RF#11 — Abandono neutro
    if session.total_messages < 3 and session.sentiment_label == SentimentLabel.NEU:
        resolution = ResolutionType.NEUTRAL
        is_abandoned = True
        auto_tags.append("abandono-neutro")

    # Frustración
    elif session.sentiment_label == SentimentLabel.NEG and (
        session.retry_count > 0
        or session.end_time is None
        or session.negative_feedback_count > 0
        or "frustracion-detectada" in session.tags
        or "bucle-detectado" in session.tags
    ):
        resolution = ResolutionType.FRUSTRATION
        auto_tags.append("frustracion-detectada")

    # Éxito
    elif (
        session.sentiment_label == SentimentLabel.POS
        or (session.star_rating is not None and session.star_rating >= 4)
        or session.positive_feedback_count > 0
    ):
        resolution = ResolutionType.SUCCESS

    # Sesión negativa sin retries → frustración leve
    elif session.sentiment_label == SentimentLabel.NEG:
        resolution = ResolutionType.FRUSTRATION

    # Default
    else:
        resolution = ResolutionType.NEUTRAL

    # Abandono por falta de end_time con muchos mensajes
    if session.end_time is None and session.total_messages >= 3:
        is_abandoned = True

    return ResolvedSession(
        **session.model_dump(),
        resolution=resolution,
        is_abandoned=is_abandoned,
        session_duration_seconds=duration,
        auto_tags=auto_tags,
    )


# ══════════════════════════════════════════════════════════════════════════
# ETAPA 5: LOAD (Warehouse)
# ══════════════════════════════════════════════════════════════════════════

async def _load(db: AsyncSession, sessions: list[ResolvedSession]) -> int:
    """Carga las sesiones resueltas al analytics_warehouse."""
    loaded = 0

    for session in sessions:
        try:
            # 1. Upsert dim_time
            time_id = await _upsert_dim_time(db, session.start_time)

            # 2. Lookup dim_language
            lang_result = await db.execute(text("""
                SELECT language_id FROM analytics_warehouse.dim_language
                WHERE iso_code = :iso
            """), {"iso": session.language_iso})
            lang_id = lang_result.scalar()

            # 3. Upsert dim_intent
            intent_id = await _upsert_dim_intent(
                db, session.intent_name, session.intent_category
            )

            # 4. Upsert dim_sentiment
            sentiment_group = {
                SentimentLabel.POS: "Positive",
                SentimentLabel.NEG: "Negative",
                SentimentLabel.NEU: "Neutral",
            }[session.sentiment_label]
            sentiment_id = await _upsert_dim_sentiment(
                db, session.sentiment_label.value, sentiment_group
            )

            # 5. Lookup resolution
            res_result = await db.execute(text("""
                SELECT resolution_id FROM analytics_warehouse.cat_resolution_types
                WHERE resolution_name = :name
            """), {"name": session.resolution.value})
            resolution_id = res_result.scalar()

            # 6. Insert fact
            fact_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO analytics_warehouse.fact_sessions_evaluation (
                    fact_id, session_id, dim_time_id, dim_language_id,
                    dim_intent_id, dim_sentiment_id, resolution_id,
                    session_duration_seconds, total_messages, sentiment_score,
                    positive_feedback_count, negative_feedback_count, is_abandoned, is_authenticated
                ) VALUES (
                    :fid, :sid, :tid, :lid, :iid, :seid, :rid,
                    :dur, :msgs, :score, :pos, :neg, :aband, :auth
                )
                ON CONFLICT DO NOTHING
            """), {
                "fid": fact_id,
                "sid": str(session.session_id),
                "tid": time_id,
                "lid": lang_id,
                "iid": intent_id,
                "seid": sentiment_id,
                "rid": resolution_id,
                "dur": session.session_duration_seconds,
                "msgs": session.total_messages,
                "score": round(session.sentiment_score, 2),
                "pos": session.positive_feedback_count,
                "neg": session.negative_feedback_count,
                "aband": session.is_abandoned,
                "auth": session.is_authenticated,
            })

            # 7. Sync tags → fact_tag_assignments
            all_tags = list(set(session.tags + session.auto_tags))
            for tag_name in all_tags:
                tag_id = await _upsert_dim_tag(db, tag_name)
                if tag_id:
                    await db.execute(text("""
                        INSERT INTO analytics_warehouse.fact_tag_assignments
                            (fact_id, tag_id)
                        VALUES (:fid, :tid)
                        ON CONFLICT DO NOTHING
                    """), {"fid": fact_id, "tid": tag_id})

            # 8. Marcar sesión como COMPLETED (4) en OLTP
            await db.execute(text("""
                UPDATE agent_core.sessions SET status_id = 4
                WHERE session_id = :sid
            """), {"sid": str(session.session_id)})

            loaded += 1

        except Exception as e:
            logger.error(
                f"Error cargando sesión {session.session_id}: {e}",
                exc_info=True,
            )
            continue

    await db.commit()
    return loaded


# ── Helpers de Upsert para dimensiones ────────────────────────────────────

async def _upsert_dim_time(db: AsyncSession, dt: datetime) -> int:
    """Upsert en dim_time y retorna time_id."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = days[dt.weekday()]
    is_weekend = dt.weekday() >= 5

    result = await db.execute(text("""
        INSERT INTO analytics_warehouse.dim_time
            (full_date, year, month, day, hour, day_of_week, is_weekend)
        VALUES (:fd, :y, :m, :d, :h, :dow, :we)
        ON CONFLICT (full_date, hour) DO UPDATE SET full_date = EXCLUDED.full_date
        RETURNING time_id
    """), {
        "fd": dt.date(),
        "y": dt.year,
        "m": dt.month,
        "d": dt.day,
        "h": dt.hour,
        "dow": dow,
        "we": is_weekend,
    })
    return result.scalar()


async def _upsert_dim_intent(db: AsyncSession, name: str, category: str) -> int:
    """Upsert en dim_intent y retorna intent_id."""
    result = await db.execute(text("""
        INSERT INTO analytics_warehouse.dim_intent (intent_name, category)
        VALUES (:name, :cat)
        ON CONFLICT (intent_name) DO UPDATE SET category = EXCLUDED.category
        RETURNING intent_id
    """), {"name": name, "cat": category})
    return result.scalar()


async def _upsert_dim_sentiment(db: AsyncSession, label: str, group: str) -> int:
    """Upsert en dim_sentiment y retorna sentiment_id."""
    result = await db.execute(text("""
        INSERT INTO analytics_warehouse.dim_sentiment (label, sentiment_group)
        VALUES (:label, :grp)
        ON CONFLICT (label) DO UPDATE SET sentiment_group = EXCLUDED.sentiment_group
        RETURNING sentiment_id
    """), {"label": label, "grp": group})
    return result.scalar()


async def _upsert_dim_tag(db: AsyncSession, tag_name: str) -> Optional[int]:
    """Upsert en dim_tags y retorna tag_id."""
    # Buscar categoría en cat_tags del OLTP
    cat_result = await db.execute(text("""
        SELECT category FROM agent_core.cat_tags WHERE tag_name = :name
    """), {"name": tag_name})
    category = cat_result.scalar() or "ia"

    result = await db.execute(text("""
        INSERT INTO analytics_warehouse.dim_tags (tag_name, category)
        VALUES (:name, :cat)
        ON CONFLICT (tag_name) DO UPDATE SET category = EXCLUDED.category
        RETURNING tag_id
    """), {"name": tag_name, "cat": category})
    return result.scalar()
