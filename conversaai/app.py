"""
Dashboard principal de ConversaAI — Consume datos desde la API de FastAPI.
Rediseñado con layout del wireframe y paleta vibrante del moodboard.
"""
import streamlit as st
import plotly.graph_objects as go
import requests
import os
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1/dashboard")

st.set_page_config(
    page_title="ConversaAI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILOS GLOBALES ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/css/materialdesignicons.min.css');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #0F1117 !important;
}

#MainMenu, footer, header { visibility: hidden !important; display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* Separación entre elementos horizontales */
[data-testid="stHorizontalBlock"] { gap: 20px !important; padding: 0 40px !important; margin-bottom: 20px !important; }
div[data-testid="column"] { padding: 0 !important; }

/* ── SIDEBAR (Fondo Oscuro Premium) ── */
[data-testid="stSidebar"] { background-color: #16181F !important; width: 260px !important; min-width: 260px !important; border-right: none !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; background-color: #16181F !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding: 0 !important; gap: 0 !important; }

.sidebar-wrap { display: flex; flex-direction: column; height: 100vh; background: #16181F; padding-top: 32px; }
.sidebar-logo { padding: 0 24px 32px; font-size: 24px; font-weight: 800; color: #F2F4F7; letter-spacing: -0.03em; display: flex; align-items: center; gap: 12px; }
.sidebar-logo i { color: #D0ED57; font-size: 28px; }
.sidebar-menu-label { font-size: 11px; font-weight: 600; letter-spacing: 0.08em; color: #62687A !important; padding: 0 24px 16px; display: block; text-transform: uppercase; }
.sidebar-nav { padding: 0 16px 8px; }
.nav-btn { 
    display: flex; align-items: center; gap: 12px; padding: 14px 20px; 
    border-radius: 16px; margin-bottom: 8px; font-size: 14px; font-weight: 600; 
    cursor: pointer; transition: all 0.2s ease; text-decoration: none !important; 
    color: #8A8F9E !important; 
}
.nav-btn i { font-size: 20px; color: #62687A !important; transition: 0.2s; }
.nav-btn:hover { background: rgba(255,255,255,0.05) !important; color: #F2F4F7 !important; }
.nav-btn:hover i { color: #A3A8B8 !important; }
.nav-btn.active { background: #D0ED57 !important; color: #16181F !important; box-shadow: 0 4px 16px rgba(208,237,87,0.15); }
.nav-btn.active i { color: #16181F !important; }

.sidebar-footer { padding: 16px; margin-top: 32px; border-top: 1px solid rgba(255,255,255,0.05); }
.logout-btn { color: #E97358 !important; }
.logout-btn i { color: #E97358 !important; }

/* ── TOPBAR (Transparente) ── */
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 32px 40px 24px; margin-bottom: 16px; }
.topbar-left { display: flex; align-items: center; gap: 24px; }
.topbar h1 { font-size: 24px; font-weight: 700; color: #F2F4F7; margin: 0; padding: 0; letter-spacing: -0.02em; }
.topbar-title-sep { width: 1px; height: 24px; background: #282C38; }
.topbar-subtitle { font-size: 14px; color: #8A8F9E; font-weight: 500; }

.topbar-right { display: flex; align-items: center; gap: 16px; }
.icon-btn { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #1A1D24; color: #F2F4F7; font-size: 20px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); transition: 0.2s; }
.icon-btn:hover { background: #282C38; }
.profile-pill { display: flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 600; color: #F2F4F7; background: #1A1D24; padding: 6px 20px 6px 6px; border-radius: 99px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); transition: 0.2s; }
.profile-pill:hover { background: #282C38; }
.profile-avatar { width: 36px; height: 36px; border-radius: 50%; background: #D0ED57; display: flex; align-items: center; justify-content: center; color: #16181F; font-size: 14px; font-weight: 700; }

/* ── UTILS ── */
.px { padding: 0 40px; margin-bottom: 32px; }

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
with st.sidebar:
    st.markdown("""
    <div class="sidebar-wrap">
        <div class="sidebar-logo">
            <i class="mdi mdi-forum"></i> ConversaAI
        </div>
        <span class="sidebar-menu-label">MENÚ PRINCIPAL</span>
        <div class="sidebar-nav">
            <a class="nav-btn active" href="/"><i class="mdi mdi-view-dashboard"></i> Dashboard</a>
            <a class="nav-btn" href="/tickets" target="_self"><i class="mdi mdi-ticket-confirmation-outline"></i> Tickets</a>
            <a class="nav-btn" href="#"><i class="mdi mdi-cog-outline"></i> Configuración</a>
        </div>
        <div class="sidebar-footer">
            <a class="nav-btn logout-btn" href="#"><i class="mdi mdi-logout"></i> Cerrar sesión</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── FETCH DATA ─────────────────────────────────────────────────────────────
data = fetch_overview()

# ── TOPBAR ─────────────────────────────────────────────────────────────────
today = datetime.now().strftime("%d/%m/%Y")
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <h1>ConversaAI</h1>
    <div class="topbar-title-sep"></div>
    <span class="topbar-subtitle">Panel de análisis</span>
  </div>
  <div class="topbar-right">
    <div class="icon-btn"><i class="mdi mdi-bell-outline"></i></div>
    <div class="profile-pill">
      <div class="profile-avatar">P</div> Pablo Diaz
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

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
