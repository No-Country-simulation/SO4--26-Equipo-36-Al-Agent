"""
Endpoints de datos para el Dashboard de Streamlit.

Todas las queries consumen exclusivamente del esquema analytics_warehouse,
respetando la restricción RF#12: sin JOINs a agent_core.session_tags.

Excepción: el detalle de chat carga mensajes desde agent_core.messages
para auditoría del Support Lead.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger("api.dashboard")

router = APIRouter(tags=["Dashboard"])


@router.get("/overview")
async def dashboard_overview(
    db: AsyncSession = Depends(get_db),
    user_filter: str = Query("all", description="all, auth, anon")
) -> dict:
    """KPIs principales, distribución de sentimiento y datos para charts."""

    auth_cond = ""
    if user_filter == "auth":
        auth_cond = "WHERE is_authenticated = TRUE"
    elif user_filter == "anon":
        auth_cond = "WHERE is_authenticated = FALSE"

    auth_cond_and = ""
    if user_filter == "auth":
        auth_cond_and = "AND is_authenticated = TRUE"
    elif user_filter == "anon":
        auth_cond_and = "AND is_authenticated = FALSE"
        
    auth_cond_and_f = ""
    if user_filter == "auth":
        auth_cond_and_f = "AND f.is_authenticated = TRUE"
    elif user_filter == "anon":
        auth_cond_and_f = "AND f.is_authenticated = FALSE"

    # Total de sesiones evaluadas
    total = await db.execute(text(f"""
        SELECT COUNT(*) FROM analytics_warehouse.fact_sessions_evaluation {auth_cond}
    """))
    total_sessions = total.scalar() or 0

    # KPIs por resolución
    resolution_counts = await db.execute(text(f"""
        SELECT cr.resolution_name, COUNT(*) AS cnt
        FROM analytics_warehouse.fact_sessions_evaluation f
        JOIN analytics_warehouse.cat_resolution_types cr ON f.resolution_id = cr.resolution_id
        WHERE 1=1 {auth_cond_and_f}
        GROUP BY cr.resolution_name
    """))
    resolutions = {r.resolution_name: r.cnt for r in resolution_counts.fetchall()}

    # Total mensajes
    total_msgs = await db.execute(text(f"""
        SELECT COALESCE(SUM(total_messages), 0)
        FROM analytics_warehouse.fact_sessions_evaluation {auth_cond}
    """))

    # Tasa de abandono
    abandoned = await db.execute(text(f"""
        SELECT COUNT(*) FROM analytics_warehouse.fact_sessions_evaluation
        WHERE is_abandoned = TRUE {auth_cond_and}
    """))

    # Tiempo promedio de respuesta (duración promedio / mensajes)
    avg_duration = await db.execute(text(f"""
        SELECT COALESCE(AVG(session_duration_seconds), 0)
        FROM analytics_warehouse.fact_sessions_evaluation
        WHERE session_duration_seconds > 0 {auth_cond_and}
    """))

    # Tickets sin leer
    unread = await db.execute(text(f"""
        SELECT COUNT(*) FROM analytics_warehouse.fact_sessions_evaluation
        WHERE is_read = FALSE {auth_cond_and}
    """))
    unread_count = unread.scalar() or 0

    # Distribución de sentimiento
    sentiment_dist = await db.execute(text(f"""
        SELECT ds.sentiment_group, COUNT(*) AS cnt
        FROM analytics_warehouse.fact_sessions_evaluation f
        JOIN analytics_warehouse.dim_sentiment ds ON f.dim_sentiment_id = ds.sentiment_id
        WHERE 1=1 {auth_cond_and_f}
        GROUP BY ds.sentiment_group
    """))
    sentiments = {r.sentiment_group: r.cnt for r in sentiment_dist.fetchall()}

    # Conversaciones por hora (hoy o último día con datos)
    by_hour = await db.execute(text(f"""
        SELECT dt.hour, COUNT(*) AS cnt
        FROM analytics_warehouse.fact_sessions_evaluation f
        JOIN analytics_warehouse.dim_time dt ON f.dim_time_id = dt.time_id
        WHERE dt.full_date = (
            SELECT MAX(full_date) FROM analytics_warehouse.dim_time dt2
            JOIN analytics_warehouse.fact_sessions_evaluation f2 ON dt2.time_id = f2.dim_time_id
        ) {auth_cond_and_f}
        GROUP BY dt.hour
        ORDER BY dt.hour
    """))
    hours_data = {r.hour: r.cnt for r in by_hour.fetchall()}

    # Top intenciones no resueltas
    top_intents = await db.execute(text(f"""
        SELECT di.intent_name, di.category, COUNT(*) AS cnt
        FROM analytics_warehouse.fact_sessions_evaluation f
        JOIN analytics_warehouse.dim_intent di ON f.dim_intent_id = di.intent_id
        JOIN analytics_warehouse.cat_resolution_types cr ON f.resolution_id = cr.resolution_id
        WHERE cr.resolution_name != 'SUCCESS' {auth_cond_and_f}
        GROUP BY di.intent_name, di.category
        ORDER BY cnt DESC
        LIMIT 5
    """))
    unresolved = [
        {"intent": r.intent_name, "category": r.category, "count": r.cnt}
        for r in top_intents.fetchall()
    ]

    abandoned_count = abandoned.scalar() or 0
    abandon_rate = round((abandoned_count / total_sessions * 100), 1) if total_sessions else 0
    success_rate = round((resolutions.get("SUCCESS", 0) / total_sessions * 100), 1) if total_sessions else 0
    frustration_rate = round((resolutions.get("FRUSTRATION", 0) / total_sessions * 100), 1) if total_sessions else 0

    return {
        "kpis": {
            "total_messages": total_msgs.scalar() or 0,
            "total_sessions": total_sessions,
            "abandon_rate": abandon_rate,
            "success_rate": success_rate,
            "frustration_rate": frustration_rate,
            "avg_duration_seconds": round(float(avg_duration.scalar() or 0), 1),
            "unread_count": unread_count,
        },
        "sentiment_distribution": sentiments,
        "conversations_by_hour": hours_data,
        "top_unresolved_intents": unresolved,
    }


@router.get("/tickets")
async def list_tickets(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sentiment: Optional[str] = Query(None),
    resolution: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user_filter: str = Query("all", description="all, auth, anon"),
) -> dict:
    """Lista tickets evaluados con filtros desde el warehouse.

    RF#12: Filtro por tags usa fact_tag_assignments + dim_tags (NO agent_core).
    """
    conditions: list[str] = []
    params: dict = {"limit": page_size, "offset": (page - 1) * page_size}

    if user_filter == "auth":
        conditions.append("f.is_authenticated = TRUE")
    elif user_filter == "anon":
        conditions.append("f.is_authenticated = FALSE")

    if sentiment:
        conditions.append("ds.sentiment_group = :sentiment")
        params["sentiment"] = sentiment

    if resolution:
        conditions.append("cr.resolution_name = :resolution")
        params["resolution"] = resolution

    if language:
        conditions.append("dl.iso_code = :language")
        params["language"] = language

    # RF#12 — Filtro por tag SOLO vía fact_tag_assignments + dim_tags
    tag_join = ""
    if tag:
        tag_join = """
            JOIN analytics_warehouse.fact_tag_assignments fta ON f.fact_id = fta.fact_id
            JOIN analytics_warehouse.dim_tags dtag ON fta.tag_id = dtag.tag_id
        """
        conditions.append("dtag.tag_name = :tag")
        params["tag"] = tag

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT f.fact_id, f.session_id, f.total_messages, f.sentiment_score,
               f.session_duration_seconds, f.is_abandoned,
               f.positive_feedback_count, f.negative_feedback_count,
               f.is_read,
               ds.label AS sentiment_label, ds.sentiment_group,
               di.intent_name, di.category AS intent_category,
               cr.resolution_name,
               dl.language_name, dl.iso_code,
               dt.full_date, dt.hour
        FROM analytics_warehouse.fact_sessions_evaluation f
        LEFT JOIN analytics_warehouse.dim_sentiment ds ON f.dim_sentiment_id = ds.sentiment_id
        LEFT JOIN analytics_warehouse.dim_intent di ON f.dim_intent_id = di.intent_id
        LEFT JOIN analytics_warehouse.cat_resolution_types cr ON f.resolution_id = cr.resolution_id
        LEFT JOIN analytics_warehouse.dim_language dl ON f.dim_language_id = dl.language_id
        LEFT JOIN analytics_warehouse.dim_time dt ON f.dim_time_id = dt.time_id
        {tag_join}
        {where}
        ORDER BY dt.full_date DESC, dt.hour DESC
        LIMIT :limit OFFSET :offset
    """

    result = await db.execute(text(query), params)
    tickets = []
    for r in result.fetchall():
        # Obtener tags para este fact (desde OLAP, NO OLTP)
        tags_q = await db.execute(text("""
            SELECT dtag.tag_name
            FROM analytics_warehouse.fact_tag_assignments fta
            JOIN analytics_warehouse.dim_tags dtag ON fta.tag_id = dtag.tag_id
            WHERE fta.fact_id = :fid
        """), {"fid": r.fact_id})
        ticket_tags = [t.tag_name for t in tags_q.fetchall()]

        tickets.append({
            "fact_id": str(r.fact_id),
            "session_id": str(r.session_id),
            "total_messages": r.total_messages,
            "sentiment_label": r.sentiment_label,
            "sentiment_group": r.sentiment_group,
            "sentiment_score": float(r.sentiment_score) if r.sentiment_score else 0,
            "intent": r.intent_name,
            "intent_category": r.intent_category,
            "resolution": r.resolution_name,
            "language": r.iso_code,
            "language_name": r.language_name,
            "date": str(r.full_date) if r.full_date else None,
            "hour": r.hour,
            "duration_seconds": r.session_duration_seconds,
            "is_abandoned": r.is_abandoned,
            "is_read": r.is_read,
            "tags": ticket_tags,
            "positive_feedback": r.positive_feedback_count,
            "negative_feedback": r.negative_feedback_count,
        })

    # Count total
    count_query = f"""
        SELECT COUNT(*) FROM analytics_warehouse.fact_sessions_evaluation f
        LEFT JOIN analytics_warehouse.dim_sentiment ds ON f.dim_sentiment_id = ds.sentiment_id
        LEFT JOIN analytics_warehouse.dim_intent di ON f.dim_intent_id = di.intent_id
        LEFT JOIN analytics_warehouse.cat_resolution_types cr ON f.resolution_id = cr.resolution_id
        LEFT JOIN analytics_warehouse.dim_language dl ON f.dim_language_id = dl.language_id
        LEFT JOIN analytics_warehouse.dim_time dt ON f.dim_time_id = dt.time_id
        {tag_join}
        {where}
    """
    total_result = await db.execute(text(count_query), params)
    total_count = total_result.scalar() or 0

    return {
        "tickets": tickets,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size,
    }


@router.get("/tickets/{session_id}")
async def ticket_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Detalle de un ticket con chat completo y análisis.

    Carga métricas desde analytics_warehouse y chat desde agent_core.messages
    (permitido para auditoría del Support Lead).
    """
    # Fact data desde warehouse
    fact_result = await db.execute(text("""
        SELECT f.*, ds.label AS sentiment_label, ds.sentiment_group,
               di.intent_name, di.category AS intent_category,
               cr.resolution_name, dl.language_name, dl.iso_code,
               dt.full_date, dt.hour
        FROM analytics_warehouse.fact_sessions_evaluation f
        LEFT JOIN analytics_warehouse.dim_sentiment ds ON f.dim_sentiment_id = ds.sentiment_id
        LEFT JOIN analytics_warehouse.dim_intent di ON f.dim_intent_id = di.intent_id
        LEFT JOIN analytics_warehouse.cat_resolution_types cr ON f.resolution_id = cr.resolution_id
        LEFT JOIN analytics_warehouse.dim_language dl ON f.dim_language_id = dl.language_id
        LEFT JOIN analytics_warehouse.dim_time dt ON f.dim_time_id = dt.time_id
        WHERE f.session_id = :sid
    """), {"sid": session_id})
    fact = fact_result.fetchone()

    if not fact:
        return {"error": "Ticket no encontrado en el warehouse"}

    # Mark as read
    if not fact.is_read:
        await db.execute(text("""
            UPDATE analytics_warehouse.fact_sessions_evaluation
            SET is_read = TRUE
            WHERE session_id = :sid
        """), {"sid": session_id})
        await db.commit()

    # Tags
    tags_q = await db.execute(text("""
        SELECT dtag.tag_name, dtag.category
        FROM analytics_warehouse.fact_tag_assignments fta
        JOIN analytics_warehouse.dim_tags dtag ON fta.tag_id = dtag.tag_id
        WHERE fta.fact_id = :fid
    """), {"fid": fact.fact_id})
    tags = [{"name": t.tag_name, "category": t.category} for t in tags_q.fetchall()]

    # Chat desde agent_core (para auditoría)
    messages_result = await db.execute(text("""
        SELECT m.message_id, cr.role_name, m.content, m.created_at
        FROM agent_core.messages m
        JOIN agent_core.cat_roles cr ON m.role_id = cr.role_id
        WHERE m.session_id = :sid
        ORDER BY m.created_at
    """), {"sid": session_id})
    messages = [
        {
            "id": str(m.message_id),
            "role": m.role_name,
            "content": m.content,
            "time": m.created_at.strftime("%H:%M") if m.created_at else "",
        }
        for m in messages_result.fetchall()
    ]

    return {
        "session_id": session_id,
        "analysis": {
            "sentiment_label": fact.sentiment_label,
            "sentiment_group": fact.sentiment_group,
            "sentiment_score": float(fact.sentiment_score) if fact.sentiment_score else 0,
            "intent": fact.intent_name,
            "intent_category": fact.intent_category,
            "resolution": fact.resolution_name,
            "language": fact.iso_code,
            "language_name": fact.language_name,
            "total_messages": fact.total_messages,
            "duration_seconds": fact.session_duration_seconds,
            "is_abandoned": fact.is_abandoned,
            "positive_feedback": fact.positive_feedback_count,
            "negative_feedback": fact.negative_feedback_count,
            "date": str(fact.full_date) if fact.full_date else None,
            "hour": fact.hour,
        },
        "tags": tags,
        "messages": messages,
    }


@router.get("/filters")
async def available_filters(db: AsyncSession = Depends(get_db)) -> dict:
    """Retorna las opciones disponibles para los filtros del dashboard."""

    sentiments = await db.execute(text("""
        SELECT DISTINCT sentiment_group FROM analytics_warehouse.dim_sentiment
        ORDER BY sentiment_group
    """))

    resolutions = await db.execute(text("""
        SELECT resolution_name FROM analytics_warehouse.cat_resolution_types
        ORDER BY resolution_name
    """))

    languages = await db.execute(text("""
        SELECT language_name, iso_code FROM analytics_warehouse.dim_language
        ORDER BY language_name
    """))

    tags = await db.execute(text("""
        SELECT tag_name, category FROM analytics_warehouse.dim_tags
        ORDER BY tag_name
    """))

    return {
        "sentiments": [r.sentiment_group for r in sentiments.fetchall()],
        "resolutions": [r.resolution_name for r in resolutions.fetchall()],
        "languages": [
            {"name": r.language_name, "code": r.iso_code}
            for r in languages.fetchall()
        ],
        "tags": [
            {"name": r.tag_name, "category": r.category}
            for r in tags.fetchall()
        ],
    }
