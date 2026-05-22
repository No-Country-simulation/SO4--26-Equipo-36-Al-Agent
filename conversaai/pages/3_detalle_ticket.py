import streamlit as st

st.set_page_config(page_title="ConversaAI — Ticket #0247", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

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
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 20px !important; padding: 0 24px 24px !important; align-items: flex-start !important; }
[data-testid="column"] { padding: 0 !important; }

/* SIDEBAR */
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
.nav-btn { display: flex; align-items: center; gap: 8px; padding: 10px 8px; border-radius: 8px; margin-bottom: 2px; font-size: 12px; text-decoration: none !important; color: #C8D4FF !important; }
.nav-btn i { font-size: 16px; color: #C8D4FF !important; }
.nav-btn.active { background: #2E52F5 !important; color: #ffffff !important; }
.nav-btn.active i { color: #ffffff !important; }
.sidebar-footer { border-top: 1px solid rgba(255,255,255,0.15); padding: 12px 8px; }

/* TOPBAR */
.topbar { background: #ffffff; display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; border-bottom: 1px solid #F0F2F8; margin-bottom: 24px; }
.topbar-left { display: flex; align-items: center; gap: 6px; }
.topbar-left h1 { font-size: 18px; font-weight: 600; color: #8892A8; margin: 0; }
.topbar-left h1 span { color: #0A1172; }
.topbar-right { display: flex; align-items: center; gap: 24px; }
.topbar-date { font-size: 11px; color: #8892A8; }
.topbar-avatar { width: 36px; height: 36px; border-radius: 50%; background: #D1F5E8; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; color: #0A5C3F; }
.badge-frustracion { display: flex; align-items: center; gap: 6px; background: #FDECEA; color: #E8593C; font-size: 12px; font-weight: 500; padding: 6px 12px; border-radius: 8px; }

/* CARD PRINCIPAL */
.ticket-card { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); padding: 14px 14px; }

/* HEADER TICKET */
.ticket-header { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid #F0F2F8; }
.ticket-header-icon { width: 36px; height: 36px; border-radius: 8px; background: #EBF0FF; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px; }
.ticket-header-info h2 { margin: 0 !important; padding: 0 !important; line-height: 1.4 !important; font-size: 14px; font-weight: 600; color: #1A2035; margin: 0; line-height: 1.3; }
.ticket-header-info p  { margin: 0 !important; padding: 0 !important; line-height: 1.4 !important; margin-bottom: 12px !important; font-size: 11px; color: #8892A8; margin: 0 0 12px 0; line-height: 1.3; }
.ticket-tags { display: flex; gap: 6px; flex-wrap: wrap; }

/* CHAT */
.chat-wrap { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }
.msg-user { align-self: flex-start; }
.msg-bot  { align-self: flex-end; }
.msg-bubble-user { background: #F0F2F8; border-radius: 12px 12px 12px 2px; padding: 10px 14px; font-size: 13px; color: #1A2035; max-width: 480px; }
.msg-bubble-bot  { background: #2E52F5; border-radius: 12px 12px 2px 12px; padding: 10px 14px; font-size: 13px; color: #ffffff; max-width: 480px; }
.msg-meta { font-size: 10px; color: #8892A8; margin-top: 4px; }

/* PENDIENTE EMOCIONAL */
.pendiente-wrap { margin-bottom: 16px; }
.pendiente-label { font-size: 12px; color: #8892A8; margin-bottom: 8px; }
.pendiente-bar { height: 8px; border-radius: 99px; background: linear-gradient(to right, #1D9E75, #F0A500, #E8593C); margin-bottom: 6px; }
.pendiente-meta { display: flex; justify-content: space-between; font-size: 10px; color: #8892A8; }

/* ALERT */
.alert-warn { background: #FFF3CC; border-radius: 8px; padding: 12px 14px; margin-top: 4px; }
.alert-warn p { font-size: 12px; color: #B07D00; margin: 0 0 4px 0; }
.alert-warn a { font-size: 12px; color: #B07D00; font-weight: 700; }

/* PANEL LATERAL */
.panel-card { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); padding: 20px; }
.panel-title { font-size: 14px; font-weight: 600; color: #1A2035; margin: 0 0 20px 0; }
.panel-row { margin-bottom: 4px; }
.panel-row-label { font-size: 11px; color: #8892A8; margin-bottom: 6px; }
.panel-row-value { font-size: 13px; font-weight: 600; color: #1A2035; }
.panel-divider { height: 1px; background: #F0F2F8; margin: 4px 0 12px; }

/* INSIGHT */
.insight-card { background: #EBF0FF; border-radius: 10px; padding: 14px; margin-top: 16px; }
.insight-header { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.insight-header span { font-size: 12px; font-weight: 600; color: #1228D4; }
.insight-body { font-size: 12px; color: #2E3A56; line-height: 1.5; }

/* TAGS */
.tag { display: inline-block; font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 99px; }
.tag-frustracion { background: #FDECEA; color: #E8593C; }
.tag-negativo    { background: #FDECEA; color: #E8593C; }
.tag-es          { background: #FFF3CC; color: #B07D00; }
.tag-canal-tg    { background: #EBF0FF; color: #2E52F5; font-weight: 600; padding: 5px 12px; border-radius: 99px; }
.tag-idioma-es   { background: #FFF3CC; color: #7A5200; }
.tag-no-match    { background: #FDECEA; color: #E8593C; }
.tag-intencion   { background: #EBF0FF; color: #2E52F5; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div class="sidebar-wrap">
        <div class="sidebar-brand"><h2>ConversaAI</h2><p>Panel de analítica</p></div>
        <span class="sidebar-menu-label">MENÚ</span>
        <div class="sidebar-nav">
            <a class="nav-btn" href="#"><i class="mdi mdi-view-dashboard-outline"></i> Dashboard</a>
            <a class="nav-btn active" href="#"><i class="mdi mdi-ticket-outline"></i> Tickets</a>
        </div>
        <div class="sidebar-footer">
            <a class="nav-btn" href="#" style="margin:0;"><i class="mdi mdi-logout"></i> Log out</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# TOPBAR
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <h1>Tickets / <span>#0247</span></h1>
  </div>
  <div class="topbar-right">
    <div class="badge-frustracion">
      <i class="mdi mdi-alert" style="font-size:14px;"></i> Frustración detectada
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# COLUMNAS PRINCIPALES
col_chat, col_panel = st.columns([2.2, 1])

with col_chat:
    st.markdown(f"""
    <div class="ticket-card">

      <!-- HEADER -->
      <div class="ticket-header">
        <div class="ticket-header-icon">{TELEGRAM_SVG}</div>
        <div class="ticket-header-info">
          <h2>Ticket #0247 — Telegram · Es</h2>
          <p>Sesión: 14 May 2026 · 13:02 hs · 7 mensajes · Abandono por timeout (15 min)</p>
          <div class="ticket-tags">
            <span class="tag tag-intencion">Consulta de estado</span>
            <span class="tag tag-negativo">Negativo</span>
            <span class="tag tag-es">Es</span>
            <span class="tag tag-frustracion">Frustración</span>
          </div>
        </div>
      </div>

      <!-- CHAT -->
      <div class="chat-wrap">
        <div class="msg-user">
          <div class="msg-bubble-user">Hola, necesito saber el estado de mi pedido</div>
          <div class="msg-meta">Usuario · 13:02</div>
        </div>
        <div class="msg-bot" style="display:flex;flex-direction:column;align-items:flex-end;">
          <div class="msg-bubble-bot">Hola! Para consultarlo necesito tu número de pedido.</div>
          <div class="msg-meta">Bot · 13:02</div>
        </div>
        <div class="msg-user">
          <div class="msg-bubble-user">Ya te lo dije, es el 845-A</div>
          <div class="msg-meta">Usuario · 13:04</div>
        </div>
        <div class="msg-bot" style="display:flex;flex-direction:column;align-items:flex-end;">
          <div class="msg-bubble-bot">No encontré resultados. ¿Podés confirmar el número?</div>
          <div class="msg-meta">Bot · 13:04</div>
        </div>
        <div class="msg-user">
          <div class="msg-bubble-user">Esto no sirve para nada, quiero hablar con alguien</div>
          <div class="msg-meta">Usuario · 13:07</div>
        </div>
      </div>

      <!-- PENDIENTE EMOCIONAL -->
      <div class="pendiente-wrap">
        <div class="pendiente-label">Pendiente emocional de la sesión</div>
        <div class="pendiente-bar"></div>
        <div class="pendiente-meta">
          <span>Neutral al inicio</span>
          <span style="color:#E8593C;">Frustración al cierre</span>
        </div>
      </div>

      <!-- ALERT -->
      <div class="alert-warn">
        <p>⚠ Clasificado como Frustración: último sentimiento negativo + loop de "no encontré" &gt;2 veces + timeout.</p>
        <a href="#">Ver RF#10 y RF#11 del ERS.</a>
      </div>

    </div>
    """, unsafe_allow_html=True)

with col_panel:
    st.markdown(f"""
    <div class="panel-card">
      <div class="panel-title">Análisis de la sesión</div>

      <div class="panel-row">
        <div class="panel-row-label">Clasificación</div>
        <span class="tag tag-frustracion">Frustración</span>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Mensajes totales</div>
        <div class="panel-row-value">7 mensajes</div>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Duración</div>
        <div class="panel-row-value">5 minutos</div>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Canal</div>
        <span class="tag tag-canal-tg">{TELEGRAM_SVG} &nbsp;Telegram</span>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Idioma detectado</div>
        <span class="tag tag-idioma-es">Español</span>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Último nodo</div>
        <span class="tag tag-no-match">no_match x3</span>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Feedback explícito</div>
        <div class="panel-row-value" style="color:#8892A8;font-weight:400;">Sin feedback</div>
      </div>

      <!-- INSIGHT -->
      <div class="insight-card">
        <div class="insight-header">
          <i class="mdi mdi-lightbulb-outline" style="color:#1228D4;font-size:16px;"></i>
          <span>Insight de la IA</span>
        </div>
        <div class="insight-body">
          El usuario repitió la consulta de estado 3 veces sin resolución. Patrón de loop detectado en nodo "no_match". Recomendación: revisar el flujo de búsqueda por número de pedido.
        </div>
      </div>

    </div>
    """, unsafe_allow_html=True)
