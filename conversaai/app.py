"""
Dashboard principal de ConversaAI — Consume datos desde la API de FastAPI.
"""
import streamlit as st
import plotly.graph_objects as go
import requests
import os

# ── CONFIG ─────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1/dashboard")

st.set_page_config(
    page_title="ConversaAI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILOS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/css/materialdesignicons.min.css');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #F8F9FC !important;
}

#MainMenu, footer, header { visibility: hidden !important; display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; padding: 0 24px !important; }
[data-testid="stHorizontalBlock"] > div:first-child { padding-right: 12px !important; }
[data-testid="stHorizontalBlock"] > div:last-child  { padding-left: 12px !important; }
[data-testid="stPlotlyChart"] > div { border-radius: 10px !important; overflow: hidden !important; background: white; box-shadow: 0 1px 4px rgba(26,32,53,0.06); }
[data-testid="stHorizontalBlock"] { margin-bottom: 24px !important; }
[data-testid="stVerticalBlockBorderWrapper"] { padding: 0 !important; }
div[data-testid="column"] { padding: 0 !important; }

[data-testid="stSidebar"] { background-color: #0D19B3 !important; width: 220px !important; min-width: 220px !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; background-color: #0D19B3 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding: 0 !important; gap: 0 !important; }
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }

.sidebar-wrap { display: flex; flex-direction: column; height: 100vh; background: #0D19B3; }
.sidebar-brand { padding: 28px 16px 12px; border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 12px; }
.sidebar-brand h2 { font-size: 16px; font-weight: 600; color: #ffffff !important; margin-bottom: 3px; margin-top: 0; }
.sidebar-brand p  { font-size: 10px; color: #C8D4FF !important; margin: 0; }
.sidebar-menu-label { font-size: 10px; font-weight: 600; letter-spacing: 0.08em; color: #ffffff !important; padding: 0 16px 8px; display: block; }
.sidebar-nav { flex: 1; padding: 0 8px; }
.nav-btn { display: flex; align-items: center; gap: 8px; padding: 10px 8px; border-radius: 8px; margin-bottom: 2px; font-size: 12px; font-weight: 400; cursor: pointer; transition: background 0.15s; text-decoration: none !important; color: #C8D4FF !important; }
.nav-btn i { font-size: 16px; color: #C8D4FF !important; }
.nav-btn:hover { background: #EBF0FF !important; color: #1228D4 !important; }
.nav-btn:hover i { color: #1228D4 !important; }
.nav-btn.active { background: #2E52F5 !important; }
.nav-btn.active, .nav-btn.active i { color: #ffffff !important; }
[data-testid="stSidebar"] .stButton button {
    background: transparent !important; color: #C8D4FF !important;
    border: none !important; border-radius: 8px !important;
    padding: 10px 8px !important; font-size: 12px !important;
    font-weight: 400 !important; text-align: left !important;
    width: 100% !important; font-family: 'Inter', sans-serif !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #EBF0FF !important; color: #1228D4 !important;
}

.topbar { background: #ffffff; display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; border-bottom: 1px solid #F0F2F8; margin-bottom: 24px; }
.topbar h1 { font-size: 18px; font-weight: 600; color: #0A1172; margin: 0 0 2px 0; line-height: 1.2; }
.topbar p  { font-size: 10px; color: #8892A8; margin: 0; line-height: 1.2; padding-bottom: 0; }

.px { padding: 0 24px; }
.mb24 { margin-bottom: 24px; }
.mb20 { margin-bottom: 20px; }

.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; }
.kpi-card { background: #fff; border-radius: 12px; padding: 16px; border-top: 3px solid #4B6BFF; box-shadow: 0 1px 4px rgba(26,32,53,0.06); }
.kpi-label { font-size: 11px; font-weight: 500; color: #8892A8; margin-bottom: 6px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1A2035; margin-bottom: 8px; line-height: 1; }
.kpi-meta  { font-size: 12px; display: flex; align-items: center; gap: 6px; }
.c-green { color: #1D9E75; } .c-red { color: #E8593C; } .c-amber { color: #F0A500; } .c-gray { color: #8892A8; }

.section-card { background: #fff; border-radius: 12px; padding: 14px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); }
.section-title { font-size: 14px; font-weight: 600; color: #1A2035; margin-bottom: 16px; }
.intent-row { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.intent-row:last-child { margin-bottom: 0; }
.intent-label { font-size: 13px; color: #2E3A56; width: 200px; flex-shrink: 0; }
.intent-bar-bg { flex: 1; height: 8px; background: #F0F2F8; border-radius: 99px; overflow: hidden; }
.intent-bar-fill { height: 100%; border-radius: 99px; }
.intent-pct { font-size: 12px; color: #8892A8; width: 50px; text-align: right; }
.no-data { padding: 40px; text-align: center; color: #8892A8; font-size: 14px; }
</style>
""", unsafe_allow_html=True)


# ── HELPER: Fetch data from API ───────────────────────────────────────────
@st.cache_data(ttl=20)
def fetch_overview() -> dict:
    """Obtiene KPIs y datos de charts desde la API."""
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
        <div class="sidebar-brand"><h2>ConversaAI</h2><p>Panel de analítica</p></div>
        <span class="sidebar-menu-label">MENÚ</span>
        <div class="sidebar-nav">
            <a class="nav-btn active" href="/"><i class="mdi mdi-view-dashboard-outline"></i> Dashboard</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎫  Tickets", key="nav_tickets"):
        st.switch_page("pages/2_tickets.py")

    st.markdown("""
    <div class="sidebar-footer">
        <a class="nav-btn" href="#" style="margin:0;"><i class="mdi mdi-logout"></i> Log out</a>
    </div>
    """, unsafe_allow_html=True)


# ── FETCH DATA ─────────────────────────────────────────────────────────────
data = fetch_overview()

# ── TOPBAR ─────────────────────────────────────────────────────────────────
from datetime import datetime
today = datetime.now().strftime("%d %b %Y")
st.markdown(f"""
<div class="topbar">
  <div><h1>Dashboard</h1><p>Monitoreo analítico · actualiza cada 20s</p></div>
  <div style="display:flex;align-items:center;gap:24px;">
    <span style="font-size:11px;color:#8892A8;">{today}</span>
    <div style="width:36px;height:36px;border-radius:50%;background:#D1F5E8;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:#0A5C3F;">P</div>
  </div>
</div>
""", unsafe_allow_html=True)


if not data:
    st.markdown('<div class="px"><div class="no-data">⚠ No se pudo conectar con la API. Verificá que el backend esté corriendo en http://localhost:8000</div></div>', unsafe_allow_html=True)
    st.stop()

kpis = data["kpis"]

# ── KPI CARDS ──────────────────────────────────────────────────────────────
success_cls = "c-green" if kpis["success_rate"] >= 50 else "c-amber"
frust_cls = "c-red" if kpis["frustration_rate"] > 20 else "c-amber"
abandon_cls = "c-red" if kpis["abandon_rate"] > 25 else "c-amber"

st.markdown(f"""
<div class="px mb24">
  <div class="kpi-grid">
    <div class="kpi-card" style="border-top-color:#2E52F5;">
      <div class="kpi-label">Mensajes totales</div><div class="kpi-value">{kpis["total_messages"]:,}</div>
      <div class="kpi-meta c-gray">Corpus evaluado</div>
    </div>
    <div class="kpi-card" style="border-top-color:#4B6BFF;">
      <div class="kpi-label">Sesiones evaluadas</div><div class="kpi-value">{kpis["total_sessions"]:,}</div>
      <div class="kpi-meta c-gray">Total procesadas</div>
    </div>
    <div class="kpi-card" style="border-top-color:#E8593C;">
      <div class="kpi-label">Tasa de abandono</div><div class="kpi-value">{kpis["abandon_rate"]}%</div>
      <div class="kpi-meta {abandon_cls}">Sesiones abandonadas</div>
    </div>
    <div class="kpi-card" style="border-top-color:#1D9E75;">
      <div class="kpi-label">Éxito confirmado</div><div class="kpi-value">{kpis["success_rate"]}%</div>
      <div class="kpi-meta {success_cls}">Resolución exitosa</div>
    </div>
    <div class="kpi-card" style="border-top-color:#F0A500;">
      <div class="kpi-label">Frustración</div><div class="kpi-value">{kpis["frustration_rate"]}%</div>
      <div class="kpi-meta {frust_cls}">Sesiones frustradas</div>
    </div>
    <div class="kpi-card" style="border-top-color:#00D4FF;">
      <div class="kpi-label">Duración promedio</div><div class="kpi-value">{int(kpis["avg_duration_seconds"])}s</div>
      <div class="kpi-meta c-gray">Segundos por sesión</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── CHARTS ROW ─────────────────────────────────────────────────────────────
col_bar, col_donut = st.columns([2.8, 1], gap="small")

with col_bar:
    hours_data = data.get("conversations_by_hour", {})
    hours = [f"{h:02d}h" for h in range(24)]
    values = [hours_data.get(str(h), hours_data.get(h, 0)) for h in range(24)]
    colors = ["#2E52F5" if v >= max(values) * 0.7 else "#A0B4FF" for v in values] if values and max(values) > 0 else ["#A0B4FF"] * 24

    fig_bar = go.Figure(go.Bar(
        x=hours, y=values,
        marker=dict(color=colors, line=dict(width=0), cornerradius=4),
    ))
    fig_bar.update_layout(
        title=dict(text="Conversaciones por hora", font=dict(size=14, family="Inter", color="#1A2035"), x=0, pad=dict(b=37)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=14, r=14, t=60, b=14), height=260,
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#8892A8"), tickcolor="white", linecolor="white"),
        yaxis=dict(showgrid=True, gridcolor="#F0F2F8", zeroline=False, tickfont=dict(size=11, color="#8892A8"), tickcolor="white", linecolor="white"),
        bargap=0.35,
    )
    st.markdown('<div style="margin:0 12px 24px 24px;">', unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_donut:
    sent = data.get("sentiment_distribution", {})
    labels = ["Positivo", "Negativo", "Neutral"]
    sent_values = [sent.get("Positive", 0), sent.get("Negative", 0), sent.get("Neutral", 0)]

    fig_donut = go.Figure(go.Pie(
        labels=labels, values=sent_values,
        hole=0.62, marker_colors=["#1D9E75", "#E8593C", "#8892A8"],
        textinfo="none", hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig_donut.update_layout(
        title=dict(text="Distribución de sentimiento", font=dict(size=14, family="Inter", color="#1A2035"), x=0),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=14, r=14, t=40, b=14), height=260,
        legend=dict(font=dict(size=12, family="Inter", color="#2E3A56"), orientation="v", x=0.55, y=0.5),
    )
    st.markdown('<div style="margin:0 24px 24px 0;">', unsafe_allow_html=True)
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ── TOP INTENCIONES NO RESUELTAS ───────────────────────────────────────────
intents = data.get("top_unresolved_intents", [])
intent_colors = ["#E8593C", "#F0A500", "#2E52F5", "#8892A8", "#A0B4FF"]

if intents:
    max_count = max(i["count"] for i in intents) if intents else 1
    intent_rows = ""
    for idx, intent in enumerate(intents):
        pct = int(intent["count"] / max_count * 100)
        color = intent_colors[idx % len(intent_colors)]
        intent_rows += f"""
        <div class="intent-row">
          <span class="intent-label">{intent["intent"]}</span>
          <div class="intent-bar-bg"><div class="intent-bar-fill" style="width:{pct}%;background:{color};"></div></div>
          <span class="intent-pct">{intent["count"]}</span>
        </div>"""

    st.markdown(f"""
    <div class="px">
      <div class="section-card mb24">
        <div class="section-title">Top intenciones no resueltas</div>
        {intent_rows}
      </div>
    </div>
    """, unsafe_allow_html=True)
