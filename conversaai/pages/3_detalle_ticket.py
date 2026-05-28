"""
Detalle de Ticket — Consume datos desde la API de FastAPI.
Muestra chat real y análisis de la sesión.
"""
import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1/dashboard"

st.set_page_config(page_title="ConversaAI — Detalle Ticket", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

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

.topbar { background: #ffffff; display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; border-bottom: 1px solid #F0F2F8; margin-bottom: 24px; }
.topbar-left h1 { font-size: 18px; font-weight: 600; color: #8892A8; margin: 0; }
.topbar-left h1 span { color: #0A1172; }

.ticket-card { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); padding: 14px; }
.ticket-header { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid #F0F2F8; }
.ticket-header-info h2 { margin: 0 !important; padding: 0 !important; font-size: 14px; font-weight: 600; color: #1A2035; }
.ticket-header-info p  { margin: 0 0 12px 0 !important; padding: 0 !important; font-size: 11px; color: #8892A8; }
.ticket-tags { display: flex; gap: 6px; flex-wrap: wrap; }

.chat-wrap { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }
.msg-user { align-self: flex-start; }
.msg-bot  { align-self: flex-end; }
.msg-bubble-user { background: #F0F2F8; border-radius: 12px 12px 12px 2px; padding: 10px 14px; font-size: 13px; color: #1A2035; max-width: 480px; }
.msg-bubble-bot  { background: #2E52F5; border-radius: 12px 12px 2px 12px; padding: 10px 14px; font-size: 13px; color: #ffffff; max-width: 480px; }
.msg-meta { font-size: 10px; color: #8892A8; margin-top: 4px; }

.panel-card { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); padding: 20px; }
.panel-title { font-size: 14px; font-weight: 600; color: #1A2035; margin: 0 0 20px 0; }
.panel-row { margin-bottom: 4px; }
.panel-row-label { font-size: 11px; color: #8892A8; margin-bottom: 6px; }
.panel-row-value { font-size: 13px; font-weight: 600; color: #1A2035; }
.panel-divider { height: 1px; background: #F0F2F8; margin: 4px 0 12px; }

.tag { display: inline-block; font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 99px; }
.tag-frustracion { background: #FDECEA; color: #E8593C; }
.tag-exito       { background: #D1F5E8; color: #1D9E75; }
.tag-neutro      { background: #F0F2F8; color: #8892A8; }
.tag-negativo    { background: #FDECEA; color: #E8593C; }
.tag-positivo    { background: #D1F5E8; color: #1D9E75; }
.tag-neutral     { background: #F0F2F8; color: #8892A8; }
.tag-idioma      { background: #FFF3CC; color: #B07D00; }
.tag-intencion   { background: #EBF0FF; color: #2E52F5; }
.tag-ia          { background: #FDECEA; color: #E8593C; }
.no-data { padding: 40px; text-align: center; color: #8892A8; font-size: 14px; }

.badge-res { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500; padding: 6px 12px; border-radius: 8px; }
.badge-FRUSTRATION { background: #FDECEA; color: #E8593C; }
.badge-SUCCESS { background: #D1F5E8; color: #1D9E75; }
.badge-NEUTRAL { background: #F0F2F8; color: #8892A8; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-wrap">
        <div class="sidebar-brand"><h2>ConversaAI</h2><p>Panel de analítica</p></div>
        <span class="sidebar-menu-label">MENÚ</span>
        <div class="sidebar-nav">
            <a class="nav-btn" href="/"><i class="mdi mdi-view-dashboard-outline"></i> Dashboard</a>
            <a class="nav-btn active" href="#"><i class="mdi mdi-ticket-outline"></i> Tickets</a>
        </div>
        <div class="sidebar-footer">
            <a class="nav-btn" href="#" style="margin:0;"><i class="mdi mdi-logout"></i> Log out</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── GET SESSION ID ─────────────────────────────────────────────────────────
session_id = st.query_params.get("session_id", None)

if not session_id:
    st.markdown('<div class="no-data">Seleccioná un ticket desde la lista de tickets para ver el detalle.</div>', unsafe_allow_html=True)
    st.stop()


# ── FETCH DATA ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_detail(sid: str) -> dict:
    try:
        resp = requests.get(f"{API_BASE}/tickets/{sid}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


data = fetch_detail(session_id)

if not data or "error" in data:
    st.markdown('<div class="no-data">⚠ Ticket no encontrado en el warehouse. Ejecutá el pipeline ETL primero.</div>', unsafe_allow_html=True)
    st.stop()

analysis = data["analysis"]
tags = data.get("tags", [])
messages = data.get("messages", [])

sid_short = session_id[:8]
resolution = analysis.get("resolution", "NEUTRAL")
res_label = {"SUCCESS": "Éxito", "FRUSTRATION": "Frustración", "NEUTRAL": "Neutro"}.get(resolution, resolution)

# ── TOPBAR ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <h1>Tickets / <span>#{sid_short}</span></h1>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <div class="badge-res badge-{resolution}">
      <i class="mdi mdi-{"alert" if resolution == "FRUSTRATION" else "check-circle" if resolution == "SUCCESS" else "minus-circle"}" style="font-size:14px;"></i>
      {res_label}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── LAYOUT ─────────────────────────────────────────────────────────────────
col_chat, col_panel = st.columns([2.2, 1])

with col_chat:
    # Tags header
    intent = analysis.get("intent", "—").replace("_", " ").title()
    sent_group = analysis.get("sentiment_group", "Neutral")
    sent_cls = {"Positive": "tag-positivo", "Negative": "tag-negativo"}.get(sent_group, "tag-neutral")
    sent_text = {"Positive": "Positivo", "Negative": "Negativo"}.get(sent_group, "Neutral")
    lang = (analysis.get("language") or "—").upper()

    tag_html = ""
    for t in tags:
        cat_cls = "tag-ia" if t.get("category") == "ia" else "tag-intencion"
        tag_html += f'<span class="tag {cat_cls}">{t["name"]}</span> '

    chat_html = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        time_str = msg.get("time", "")
        role_label = "Usuario" if role == "user" else "Bot"

        if role == "user":
            chat_html += f'''
            <div class="msg-user">
              <div class="msg-bubble-user">{content}</div>
              <div class="msg-meta">{role_label} · {time_str}</div>
            </div>'''
        else:
            chat_html += f'''
            <div class="msg-bot" style="display:flex;flex-direction:column;align-items:flex-end;">
              <div class="msg-bubble-bot">{content}</div>
              <div class="msg-meta">{role_label} · {time_str}</div>
            </div>'''

    st.markdown(f"""
    <div class="ticket-card">
      <div class="ticket-header">
        <div class="ticket-header-info">
          <h2>Ticket #{sid_short} — {analysis.get("language_name", "")} · {analysis.get("date", "")}</h2>
          <p>{analysis.get("total_messages", 0)} mensajes · {analysis.get("duration_seconds", 0)}s de duración</p>
          <div class="ticket-tags">
            <span class="tag tag-intencion">{intent}</span>
            <span class="tag {sent_cls}">{sent_text}</span>
            <span class="tag tag-idioma">{lang}</span>
            {tag_html}
          </div>
        </div>
      </div>
      <div class="chat-wrap">
        {chat_html if chat_html else '<div class="no-data">Sin mensajes disponibles</div>'}
      </div>
    </div>
    """, unsafe_allow_html=True)


with col_panel:
    res_cls = {"SUCCESS": "tag-exito", "FRUSTRATION": "tag-frustracion"}.get(resolution, "tag-neutro")

    fb_text = "Sin feedback"
    if analysis.get("positive_feedback", 0) > 0:
        fb_text = f"👍 {analysis['positive_feedback']} positivos"
    elif analysis.get("negative_feedback", 0) > 0:
        fb_text = f"👎 {analysis['negative_feedback']} negativos"

    st.markdown(f"""
    <div class="panel-card">
      <div class="panel-title">Análisis de la sesión</div>

      <div class="panel-row">
        <div class="panel-row-label">Clasificación</div>
        <span class="tag {res_cls}">{res_label}</span>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Sentimiento</div>
        <span class="tag {sent_cls}">{sent_text} ({analysis.get("sentiment_score", 0):.2f})</span>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Intención detectada</div>
        <span class="tag tag-intencion">{intent}</span>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Mensajes totales</div>
        <div class="panel-row-value">{analysis.get("total_messages", 0)} mensajes</div>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Duración</div>
        <div class="panel-row-value">{analysis.get("duration_seconds", 0)}s</div>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Idioma detectado</div>
        <span class="tag tag-idioma">{analysis.get("language_name", "—")}</span>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Abandono</div>
        <div class="panel-row-value">{"Sí ⚠" if analysis.get("is_abandoned") else "No ✓"}</div>
      </div>
      <div class="panel-divider"></div>

      <div class="panel-row">
        <div class="panel-row-label">Feedback explícito</div>
        <div class="panel-row-value" style="color:#8892A8;font-weight:400;">{fb_text}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
