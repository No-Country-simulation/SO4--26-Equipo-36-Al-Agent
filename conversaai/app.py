"""
Dashboard principal de ConversaAI — Consume datos desde la API de FastAPI.
Rediseñado con layout del wireframe y paleta vibrante del moodboard.
"""
import streamlit as st
import plotly.graph_objects as go
import requests
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ── CONFIG ─────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1/dashboard")

st.set_page_config(
    page_title="ConversaAI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

from layout import load_global_css, render_sidebar, render_topbar

# ── ESTILOS GLOBALES Y COMPONENTES UI ──────────────────────────────────────
load_global_css()

st.markdown("""
<style>

/* ── KPI CARDS ── */
.kpi-grid { display: grid; gap: 20px; margin-bottom: 20px; }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.kpi-card { 
    background: #1A1D24; border-radius: 24px; padding: 28px; 
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    display: flex; flex-direction: column; justify-content: space-between;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid rgba(255,255,255,0.02); position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.05); }
.kpi-card.highlight { background: #D0ED57; box-shadow: 0 8px 32px rgba(208, 237, 87, 0.15); border: none; }

.kpi-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.kpi-icon-box { width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.kpi-label { font-size: 14px; font-weight: 600; color: #8A8F9E; }
.highlight .kpi-label { color: #4A5426; }
.kpi-value { font-size: 42px; font-weight: 800; color: #F2F4F7; margin-bottom: 12px; line-height: 1; letter-spacing: -0.03em; }
.highlight .kpi-value { color: #16181F; }
.kpi-meta  { font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 6px; color: #8A8F9E; }
.highlight .kpi-meta { color: #16181F; opacity: 0.8; }
.meta-icon { font-size: 18px; }

/* Colores de Cajas de Iconos en Dark Mode */
.bg-blue { background: rgba(155,169,255,0.15); } .c-blue { color: #9BA9FF; }
.bg-purple { background: rgba(182,160,255,0.15); } .c-purple { color: #B6A0FF; }
.bg-red { background: rgba(233,115,88,0.15); } .c-red-icon { color: #E97358; }
.bg-orange { background: rgba(244,162,97,0.15); } .c-orange { color: #F4A261; }
.bg-green { background: rgba(29,158,117,0.15); } .c-green-icon { color: #1D9E75; }
.bg-dark { background: #16181F; } .c-lime { color: #D0ED57; }

.c-green { color: #D0ED57; } .c-red { color: #E97358; } .c-amber { color: #F4A261; }

/* ── CHARTS PLOTLY CSS ── */
[data-testid="stPlotlyChart"] > div { 
    background: #1A1D24 !important; 
    border-radius: 24px !important; 
    box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important;
    border: 1px solid rgba(255,255,255,0.02) !important;
    overflow: hidden !important;
}

/* ── INTENTS (Sección Inferior) ── */
.section-card { background: #1A1D24; border-radius: 24px; padding: 32px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.02); margin: 0 40px 40px; }
.section-title { font-size: 18px; font-weight: 700; color: #F2F4F7; margin-bottom: 28px; }
.intent-row { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
.intent-row:last-child { margin-bottom: 0; }
.intent-label { font-size: 14px; font-weight: 600; color: #F2F4F7; width: 180px; flex-shrink: 0; }
.intent-bar-bg { flex: 1; height: 14px; background: #282C38; border-radius: 99px; overflow: hidden; }
.intent-bar-fill { height: 100%; border-radius: 99px; }
.intent-pct { font-size: 14px; font-weight: 700; color: #F2F4F7; width: 44px; text-align: right; }
.no-data { padding: 40px; text-align: center; color: #8A8F9E; font-size: 14px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# ── HELPER: Fetch data from API ───────────────────────────────────────────
@st.cache_data(ttl=20)
def fetch_overview() -> dict:
    try:
        resp = requests.get(f"{API_BASE}/overview", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


# ── SIDEBAR ────────────────────────────────────────────────────────────────
render_sidebar(active_page="dashboard")


# ── POLLING & ESTADO DE NOTIFICACIONES ─────────────────────────────────────
st_autorefresh(interval=10000, key="dash_refresh")

if "dash_last_count" not in st.session_state:
    st.session_state.dash_last_count = -1
if "has_notifications" not in st.session_state:
    st.session_state.has_notifications = False

# ── FETCH DATA ─────────────────────────────────────────────────────────────
data = fetch_overview()

if data:
    current_count = data.get("kpis", {}).get("total_sessions", 0)
    if st.session_state.dash_last_count != -1 and current_count > st.session_state.dash_last_count:
        st.toast("¡Nuevo ticket clasificado!", icon="🔔")
        st.session_state.has_notifications = True
    st.session_state.dash_last_count = current_count

# ── TOPBAR ─────────────────────────────────────────────────────────────────
today = datetime.now().strftime("%d/%m/%Y")
render_topbar(subtitle="Panel de análisis", has_notifications=st.session_state.has_notifications)

if not data:
    st.markdown('<div class="px"><div class="no-data">⚠ No se pudo conectar con la API.</div></div>', unsafe_allow_html=True)
    st.stop()

kpis = data["kpis"]

# ── KPI CARDS ──────────────────────────────────────────────────────────────
abandon_cls = "c-red" if kpis["abandon_rate"] > 25 else "c-amber"
frust_cls = "c-red" if kpis["frustration_rate"] > 20 else "c-amber"

st.markdown(f"""
<div class="px">
<div class="kpi-grid grid-3">
<div class="kpi-card">
    <div class="kpi-header">
        <div class="kpi-label">Mensajes hoy - {today}</div>
        <div class="kpi-icon-box bg-blue"><i class="mdi mdi-message-text-outline c-blue"></i></div>
    </div>
    <div class="kpi-value">{kpis["total_messages"]:,}</div>
    <div class="kpi-meta"><i class="mdi mdi-arrow-up-circle-outline meta-icon"></i> + 12% vs ayer</div>
</div>

<div class="kpi-card">
    <div class="kpi-header">
        <div class="kpi-label">Conversaciones finalizadas</div>
        <div class="kpi-icon-box bg-purple"><i class="mdi mdi-robot-outline c-purple"></i></div>
    </div>
    <div class="kpi-value">{kpis["total_sessions"]:,}</div>
    <div class="kpi-meta"><i class="mdi mdi-filter-variant meta-icon"></i> 11 resoluciones automatizadas</div>
</div>

<div class="kpi-card">
    <div class="kpi-header">
        <div class="kpi-label">Tasa de abandono</div>
        <div class="kpi-icon-box bg-red"><i class="mdi mdi-door-open c-red-icon"></i></div>
    </div>
    <div class="kpi-value">{kpis["abandon_rate"]}%</div>
    <div class="kpi-meta {abandon_cls}"><i class="mdi mdi-alert-circle-outline meta-icon"></i> + 4% esta semana</div>
</div>
</div>

<div class="kpi-grid grid-3">
<div class="kpi-card highlight">
    <div class="kpi-header">
        <div class="kpi-label">Éxito confirmado</div>
        <div class="kpi-icon-box bg-dark"><i class="mdi mdi-check-decagram c-lime"></i></div>
    </div>
    <div class="kpi-value">{kpis["success_rate"]}%</div>
    <div class="kpi-meta"><i class="mdi mdi-arrow-up-circle-outline meta-icon"></i> + 2% respecto al mes pasado</div>
</div>

<div class="kpi-card">
    <div class="kpi-header">
        <div class="kpi-label">Tasa de frustración</div>
        <div class="kpi-icon-box bg-orange"><i class="mdi mdi-emoticon-sad-outline c-orange"></i></div>
    </div>
    <div class="kpi-value">{kpis["frustration_rate"]}%</div>
    <div class="kpi-meta {frust_cls}"><i class="mdi mdi-alert-outline meta-icon"></i> + 1% en la última hora</div>
</div>

<div class="kpi-card">
    <div class="kpi-header">
        <div class="kpi-label">Tiempo de respuesta</div>
        <div class="kpi-icon-box bg-green"><i class="mdi mdi-timer-outline c-green-icon"></i></div>
    </div>
    <div class="kpi-value">1.4s</div>
    <div class="kpi-meta c-green"><i class="mdi mdi-check meta-icon"></i> Objetivo alcanzado (&lt;2s)</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ── CHARTS ROW ─────────────────────────────────────────────────────────────
# Usamos columnas de Streamlit. Gracias al CSS, el contenedor de Plotly será una tarjeta blanca.
col_bar, col_donut = st.columns([2.5, 1], gap="small")

with col_bar:
    hours_data = data.get("conversations_by_hour", {})
    hours = [f"{h:02d}h" for h in range(24)]
    values = [hours_data.get(str(h), hours_data.get(h, 0)) for h in range(24)]
    
    # Paleta vibrante para barras en Dark Mode
    max_val = max(values) if values else 1
    colors = ["#9BA9FF" if v >= max_val * 0.7 else "#282C38" for v in values]

    fig_bar = go.Figure(go.Bar(
        x=hours, y=values,
        marker=dict(color=colors, line=dict(width=0), cornerradius=8),
    ))
    fig_bar.update_layout(
        title=dict(text=f"Conversaciones por hora - Hoy {today}", font=dict(size=15, family="Inter", color="#F2F4F7"), x=0, pad=dict(b=0)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=24, t=74, b=40), height=340,
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#8A8F9E", family="Inter"), tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        bargap=0.3,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

with col_donut:
    sent = data.get("sentiment_distribution", {})
    labels = ["Positivo", "Negativo", "Neutral"]
    sent_values = [sent.get("Positive", 0), sent.get("Negative", 0), sent.get("Neutral", 0)]

    # Colores Moodboard vibrante: #D0ED57, #E97358, #E0E4ED
    fig_donut = go.Figure(go.Pie(
        labels=labels, values=sent_values,
        hole=0.6, marker=dict(colors=["#D0ED57", "#E97358", "#282C38"], line=dict(color="#1A1D24", width=2)),
        textinfo="none", hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig_donut.update_layout(
        title=dict(text="Distribución de sentimiento", font=dict(size=15, family="Inter", color="#F2F4F7"), x=0, pad=dict(b=0)),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=24, r=24, t=74, b=40), height=340,
        showlegend=True,
        legend=dict(font=dict(size=12, family="Inter", color="#8A8F9E"), orientation="h", x=0.5, y=-0.2, xanchor="center"),
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})


# ── TOP INTENCIONES NO RESUELTAS ───────────────────────────────────────────
intents = data.get("top_unresolved_intents", [])
intent_colors = ["#E97358", "#F4A261", "#9BA9FF", "#1D9E75", "#D0ED57"]

if intents:
    max_count = max(i["count"] for i in intents) if intents else 1
    intent_rows = ""
    for idx, intent in enumerate(intents):
        pct = int(intent["count"] / max_count * 100)
        color = intent_colors[idx % len(intent_colors)] if idx < len(intent_colors) else "#E0E4ED"
        intent_rows += f'<div class="intent-row"><span class="intent-label">{intent["intent"].replace("_", " ").title()}</span><div class="intent-bar-bg"><div class="intent-bar-fill" style="width:{pct}%;background:{color};"></div></div><span class="intent-pct">{pct}%</span></div>'

    html_block = f'<div class="section-card"><div class="section-title">Top intenciones no resueltas</div>{intent_rows}</div>'
    st.markdown(html_block, unsafe_allow_html=True)
