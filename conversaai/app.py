import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="ConversaAI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

TELEGRAM_SVG = """<svg width="14" height="13" viewBox="0 0 11 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M9.48532 0.0906039C7.5813 1.1182 2.29404 3.97121 0.397196 4.99465C0.141714 5.1326 -0.0121029 5.40396 0.000746782 5.69383C0.0139744 5.98333 0.191599 6.24031 0.458041 6.35445L3.01966 7.45385L3.0072 9.06044C3.00455 9.37299 3.19502 9.65531 3.48641 9.76945C3.77742 9.88396 4.10924 9.80724 4.32051 9.5767L5.40253 8.39453L8.1603 9.30723C8.3674 9.37601 8.59454 9.35145 8.78237 9.23996C8.97058 9.12885 9.10135 8.94177 9.14103 8.72673L10.5874 0.893329C10.6403 0.607234 10.5243 0.316231 10.2892 0.14465C10.0537 -0.026553 9.74118 -0.0473412 9.48532 0.0906039ZM9.7272 1.39031L8.39764 8.58954L5.40782 7.60011C5.26647 7.55325 5.11076 7.59407 5.01023 7.70367L3.76306 9.06611L3.77628 7.36277L9.7272 1.39031ZM0.755855 5.65981L3.31294 6.75695L8.6501 1.40014L0.755855 5.65981Z" fill="#4B6BFF"/></svg>"""

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

/* Eliminar todo padding de Streamlit */
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; padding: 0 24px !important; }
[data-testid="stHorizontalBlock"] > div:first-child { padding-right: 12px !important; }
[data-testid="stHorizontalBlock"] > div:last-child  { padding-left: 12px !important; }

/* Border-radius en contenedores de Plotly */
[data-testid="stPlotlyChart"] > div { border-radius: 10px !important; overflow: hidden !important; background: white; box-shadow: 0 1px 4px rgba(26,32,53,0.06); }

/* Separación entre charts y secciones de abajo */
[data-testid="stHorizontalBlock"] { margin-bottom: 24px !important; }
[data-testid="stVerticalBlockBorderWrapper"] { padding: 0 !important; }
div[data-testid="column"] { padding: 0 !important; }

/* ── SIDEBAR ── */
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
    background: transparent !important;
    color: #C8D4FF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 8px !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    text-align: left !important;
    width: 100% !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #EBF0FF !important;
    color: #1228D4 !important;
}

/* ── TOPBAR ── */
.topbar { background: #ffffff; display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; border-bottom: 1px solid #F0F2F8; margin-bottom: 24px; }
.topbar h1 { font-size: 18px; font-weight: 600; color: #0A1172; margin: 0 0 2px 0; line-height: 1.2; }
.topbar p  { font-size: 10px; color: #8892A8; margin: 0; line-height: 1.2; padding-bottom: 0; }
.topbar-right { display: flex; align-items: center; gap: 24px; }
.topbar-date { font-size: 11px; color: #8892A8; }
.topbar-avatar { width: 36px; height: 36px; border-radius: 50%; background: #D1F5E8; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; color: #0A5C3F; }

/* ── CONTENT ── */
.px { padding: 0 24px; }
.mb24 { margin-bottom: 24px; }
.mb20 { margin-bottom: 20px; }

/* KPI */
.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; }
.kpi-card { background: #fff; border-radius: 12px; padding: 16px; border-top: 3px solid #4B6BFF; box-shadow: 0 1px 4px rgba(26,32,53,0.06); }
.kpi-label { font-size: 11px; font-weight: 500; color: #8892A8; margin-bottom: 6px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1A2035; margin-bottom: 8px; line-height: 1; }
.kpi-meta  { font-size: 12px; display: flex; align-items: center; gap: 6px; }
.c-green { color: #1D9E75; } .c-red { color: #E8593C; } .c-amber { color: #F0A500; } .c-gray { color: #8892A8; }

/* CARDS */
.section-card { background: #fff; border-radius: 12px; padding: 14px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); }
.chart-card   { background: #fff; border-radius: 10px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); overflow: hidden; }
.charts-row-wrap { padding: 0 24px; margin-bottom: 24px; display: flex; gap: 24px; }
.charts-row-wrap > div:first-child { flex: 2.8; min-width: 0; }
.charts-row-wrap > div:last-child  { flex: 1; min-width: 0; }

.section-title { font-size: 14px; font-weight: 600; color: #1A2035; margin-bottom: 16px; }
.intent-row { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.intent-row:last-child { margin-bottom: 0; }
.intent-label { font-size: 13px; color: #2E3A56; width: 150px; flex-shrink: 0; }
.intent-bar-bg { flex: 1; height: 8px; background: #F0F2F8; border-radius: 99px; overflow: hidden; }
.intent-bar-fill { height: 100%; border-radius: 99px; }
.intent-pct { font-size: 12px; color: #8892A8; width: 36px; text-align: right; }

.tickets-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.tickets-header span { font-size: 14px; font-weight: 600; color: #1A2035; }
.tickets-header a { font-size: 13px; color: #2E52F5; text-decoration: none; }
.ticket-row { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #F0F2F8; }
.ticket-row:last-child { border-bottom: none; }
.ticket-left { display: flex; align-items: center; gap: 10px; }
.ticket-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.ticket-icon.tg { background: #EBF0FF; } .ticket-icon.wa { background: #D1F5E8; }
.ticket-id   { font-size: 13px; font-weight: 600; color: #1A2035; }
.ticket-time { font-size: 11px; color: #8892A8; font-weight: 400; }
.ticket-msg  { font-size: 12px; color: #2E3A56; margin-top: 2px; }
.tag { font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 99px; }
.tag-neg { background: #FDECEA; color: #E8593C; }
.tag-pos { background: #D1F5E8; color: #1D9E75; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-wrap">
        <div class="sidebar-brand"><h2>ConversaAI</h2><p>Panel de analítica</p></div>
        <span class="sidebar-menu-label">MENÚ</span>
        <div class="sidebar-nav">
            <a class="nav-btn active" href="#"><i class="mdi mdi-view-dashboard-outline"></i> Dashboard</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    [data-testid="stSidebar"] .stButton button {
        background: transparent !important; color: #C8D4FF !important;
        border: none !important; border-radius: 8px !important;
        padding: 10px 8px !important; font-size: 12px !important;
        font-weight: 400 !important; text-align: left !important;
        width: 100% !important; font-family: 'Inter', sans-serif !important;
        box-shadow: none !important; margin: 0 0 2px 0 !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: #EBF0FF !important; color: #1228D4 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("🎫  Tickets", key="nav_tickets"):
        st.markdown('<meta http-equiv="refresh" content="0; url=/2_tickets">', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-footer">
        <a class="nav-btn" href="#" style="margin:0;"><i class="mdi mdi-logout"></i> Log out</a>
    </div>
    """, unsafe_allow_html=True)

# ── TOPBAR ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div><h1>Dashboard</h1><p>Monitoreo en tiempo real · actualiza cada 20s</p></div>
  <div class="topbar-right">
    <span class="topbar-date">14 May 2026</span>
    <div class="topbar-avatar">P</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="px mb24">
  <div class="kpi-grid">
    <div class="kpi-card" style="border-top-color:#2E52F5;">
      <div class="kpi-label">Mensajes hoy</div><div class="kpi-value">247</div>
      <div class="kpi-meta c-green">↑ +12% vs ayer</div>
    </div>
    <div class="kpi-card" style="border-top-color:#4B6BFF;">
      <div class="kpi-label">Sesiones activas</div><div class="kpi-value">18</div>
      <div class="kpi-meta c-gray">{TELEGRAM_SVG} 11 &nbsp;·&nbsp; <i class="mdi mdi-whatsapp" style="color:#1D9E75;font-size:15px;"></i> 7</div>
    </div>
    <div class="kpi-card" style="border-top-color:#E8593C;">
      <div class="kpi-label">Tasa de abandono</div><div class="kpi-value">23%</div>
      <div class="kpi-meta c-red">↑ +4% esta semana</div>
    </div>
    <div class="kpi-card" style="border-top-color:#1D9E75;">
      <div class="kpi-label">Éxito confirmado</div><div class="kpi-value">61%</div>
      <div class="kpi-meta c-green">↑ +2%</div>
    </div>
    <div class="kpi-card" style="border-top-color:#F0A500;">
      <div class="kpi-label">Frustración</div><div class="kpi-value">16%</div>
      <div class="kpi-meta c-amber">↑ +1%</div>
    </div>
    <div class="kpi-card" style="border-top-color:#00D4FF;">
      <div class="kpi-label">Tiempo respuesta</div><div class="kpi-value">1.4s</div>
      <div class="kpi-meta c-green">Objetivo &lt;2s ✓</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── CHARTS ROW ─────────────────────────────────────────────────────────────
col_bar, col_donut = st.columns([2.8, 1], gap="small")

with col_bar:
    hours  = ["00h","02h","04h","06h","08h","10h","12h","14h","16h","18h","20h","22h","23h"]
    values = [12, 8, 5, 9, 28, 42, 61, 55, 48, 31, 38, 45, 40]
    colors = ["#2E52F5" if v >= 55 else "#A0B4FF" for v in values]
    fig_bar = go.Figure(go.Bar(
        x=hours, y=values,
        marker=dict(color=colors, line=dict(width=0), cornerradius=4),
    ))
    fig_bar.update_layout(
        title=dict(text="Conversaciones por hora — hoy", font=dict(size=14, family="Inter", color="#1A2035"), x=0, pad=dict(b=37)),
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
    fig_donut = go.Figure(go.Pie(
        labels=["Positivo","Negativo","Neutral"], values=[60, 21, 19],
        hole=0.62, marker_colors=["#1D9E75","#E8593C","#8892A8"],
        textinfo="none", hovertemplate="%{label}: %{value}%<extra></extra>",
    ))
    fig_donut.update_layout(
        title=dict(text="Distribución de sentimiento", font=dict(size=14, family="Inter", color="#1A2035"), x=0),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=14, r=14, t=40, b=14), height=260,
        legend=dict(font=dict(size=12, family="Inter", color="#2E3A56"), orientation="v", x=0.55, y=0.5),
    )
    st.markdown('<div style="margin:0 24px 24px 0;">', unsafe_allow_html=True)
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── INTENCIONES + TICKETS ──────────────────────────────────────────────────
st.markdown(f"""
<div class="px">
  <div class="section-card mb20">
    <div class="section-title">Top intenciones no resueltas</div>
    <div class="intent-row">
      <span class="intent-label">Consulta de estado</span>
      <div class="intent-bar-bg"><div class="intent-bar-fill" style="width:72%;background:#E8593C;"></div></div>
      <span class="intent-pct">72%</span>
    </div>
    <div class="intent-row">
      <span class="intent-label">Solicitar operador</span>
      <div class="intent-bar-bg"><div class="intent-bar-fill" style="width:55%;background:#F0A500;"></div></div>
      <span class="intent-pct">55%</span>
    </div>
    <div class="intent-row">
      <span class="intent-label">Reclamo por error</span>
      <div class="intent-bar-bg"><div class="intent-bar-fill" style="width:38%;background:#2E52F5;"></div></div>
      <span class="intent-pct">38%</span>
    </div>
  </div>

  <div class="section-card mb24">
    <div class="tickets-header">
      <span>Últimos tickets</span>
      <a href="#">Ver todos →</a>
    </div>
    <div class="ticket-row">
      <div class="ticket-left">
        <div class="ticket-icon tg">{TELEGRAM_SVG}</div>
        <div>
          <div class="ticket-id">#0247 · <span class="ticket-time">3 min</span></div>
          <div class="ticket-msg">No me aparece el estado de mi pedido...</div>
        </div>
      </div>
      <span class="tag tag-neg">negativo</span>
    </div>
    <div class="ticket-row">
      <div class="ticket-left">
        <div class="ticket-icon wa"><i class="mdi mdi-whatsapp" style="color:#1D9E75;font-size:15px;"></i></div>
        <div>
          <div class="ticket-id">#0246 · <span class="ticket-time">8 min</span></div>
          <div class="ticket-msg">Joyita, gracias! me ayudó mucho</div>
        </div>
      </div>
      <span class="tag tag-pos">positivo</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
