"""
Página de Tickets — Consume datos desde la API de FastAPI.
Rediseñado con layout del wireframe y paleta vibrante del moodboard.
"""
import streamlit as st
import requests
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1/dashboard")

st.set_page_config(page_title="ConversaAI — Tickets", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/css/materialdesignicons.min.css');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #F0F2F5 !important;
}

#MainMenu, footer, header { visibility: hidden !important; display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 16px !important; padding: 0 40px 24px !important; align-items: center !important; }
[data-testid="column"] { padding: 0 !important; }

/* ── SIDEBAR (Fondo Oscuro Premium) ── */
[data-testid="stSidebar"] { background-color: #1A1C23 !important; width: 260px !important; min-width: 260px !important; border-right: none !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; background-color: #1A1C23 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding: 0 !important; gap: 0 !important; }
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }

.sidebar-wrap { display: flex; flex-direction: column; height: 100vh; background: #1A1C23; padding-top: 32px; }
.sidebar-logo { padding: 0 24px 32px; font-size: 24px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.03em; display: flex; align-items: center; gap: 12px; }
.sidebar-logo i { color: #D0ED57; font-size: 28px; }
.sidebar-menu-label { font-size: 11px; font-weight: 600; letter-spacing: 0.08em; color: #62687A !important; padding: 0 24px 16px; display: block; text-transform: uppercase; }
.sidebar-nav { padding: 0 16px 8px; }
.nav-btn { 
    display: flex; align-items: center; gap: 12px; padding: 14px 20px; 
    border-radius: 16px; margin-bottom: 8px; font-size: 14px; font-weight: 600; 
    cursor: pointer; transition: all 0.2s ease; text-decoration: none !important; 
    color: #A3A8B8 !important; 
}
.nav-btn i { font-size: 20px; color: #62687A !important; transition: 0.2s; }
.nav-btn:hover { background: rgba(255,255,255,0.05) !important; color: #FFFFFF !important; }
.nav-btn:hover i { color: #A3A8B8 !important; }
.nav-btn.active { background: #D0ED57 !important; color: #1A1C23 !important; box-shadow: 0 4px 16px rgba(208,237,87,0.15); }
.nav-btn.active i { color: #1A1C23 !important; }

.sidebar-footer { padding: 16px; margin-top: 32px; border-top: 1px solid rgba(255,255,255,0.05); }
.logout-btn { color: #E97358 !important; }
.logout-btn i { color: #E97358 !important; }

/* ── TOPBAR ── */
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 32px 40px 24px; margin-bottom: 16px; }
.topbar-left { display: flex; align-items: center; gap: 24px; }
.topbar h1 { font-size: 24px; font-weight: 700; color: #1A1C23; margin: 0; padding: 0; letter-spacing: -0.02em; }

.topbar-right { display: flex; align-items: center; gap: 16px; }
.icon-btn { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #FFFFFF; color: #1A1C23; font-size: 20px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.03); transition: 0.2s; }
.icon-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.06); }
.profile-pill { display: flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 600; color: #1A1C23; background: #FFFFFF; padding: 6px 20px 6px 6px; border-radius: 99px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.03); transition: 0.2s; }
.profile-pill:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.06); }
.profile-avatar { width: 36px; height: 36px; border-radius: 50%; background: #1A1C23; display: flex; align-items: center; justify-content: center; color: #D0ED57; font-size: 14px; font-weight: 700; }

/* ── FILTERS (Pills Design) ── */
[data-testid="stTextInput"] { margin: 0 !important; }
[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] > div { border: none !important; box-shadow: none !important; background: transparent !important; }
[data-testid="stTextInput"] > div > div { 
    background: #FFFFFF !important; border: none !important; 
    border-radius: 99px !important; height: 48px !important; min-height: 48px !important; 
    padding: 0 24px !important; box-shadow: 0 4px 16px rgba(0,0,0,0.03) !important; 
}
[data-testid="stTextInput"] input { font-size: 14px !important; color: #1A1C23 !important; font-family: 'Inter', sans-serif !important; background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; height: 48px !important; }

[data-testid="stSelectbox"] { margin: 0 !important; }
[data-testid="stSelectbox"] label { display: none !important; }
[data-testid="stSelectbox"] > div > div { 
    background: #FFFFFF !important; border: none !important; 
    border-radius: 99px !important; height: 48px !important; min-height: 48px !important; 
    font-size: 14px !important; font-weight: 500 !important; color: #1A1C23 !important; 
    font-family: 'Inter', sans-serif !important; padding: 0 20px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.03) !important;
}

/* ── TICKETS LIST (Cards Design) ── */
.table-wrap { padding: 0 40px 40px; }
.tickets-summary { display: flex; gap: 12px; margin-bottom: 24px; padding: 0 40px; }
.summary-pill { font-size: 14px; font-weight: 500; color: #1A1C23; background: #FFFFFF; padding: 10px 20px; border-radius: 99px; box-shadow: 0 4px 16px rgba(0,0,0,0.03); display: flex; gap: 8px; align-items: center; }
.summary-pill span { font-weight: 800; }

.ticket-card { 
    background: #FFFFFF; border-radius: 20px; margin-bottom: 16px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.03); overflow: hidden;
    display: flex; align-items: center; justify-content: space-between;
    padding: 24px 32px; transition: transform 0.2s, box-shadow 0.2s;
    border: none; cursor: pointer;
}
.ticket-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.05); }

.ticket-main { display: flex; align-items: center; gap: 24px; flex: 1; }
.ticket-icon { 
    width: 56px; height: 56px; border-radius: 50%; display: flex; 
    align-items: center; justify-content: center; font-size: 28px; flex-shrink: 0;
}
.icon-pos { background: #EBF8B8; color: #4A5426; }
.icon-neg { background: #FDEEEB; color: #E97358; }
.icon-neu { background: #F0F2F5; color: #62687A; }

.ticket-info { display: flex; flex-direction: column; gap: 8px; }
.ticket-id { font-size: 16px; font-weight: 700; color: #1A1C23; display: flex; align-items: center; gap: 10px; }
.ticket-time { font-size: 14px; font-weight: 500; color: #8A8F9E; }
.ticket-intent { font-size: 15px; color: #62687A; }

.ticket-tags { display: flex; align-items: center; gap: 12px; }
.tag { 
    display: inline-flex; align-items: center; font-size: 13px; font-weight: 700; 
    padding: 8px 16px; border-radius: 99px; white-space: nowrap; text-transform: uppercase; letter-spacing: 0.05em;
}
.tag-intencion   { background: #F0F2F5; color: #1A1C23; }
.tag-positivo    { background: #D0ED57; color: #1A1C23; }
.tag-neutral     { background: #F0F2F5; color: #62687A; }
.tag-negativo    { background: #FDEEEB; color: #E97358; }
.tag-idioma      { background: #1A1C23; color: #ffffff; }

.no-results { padding: 60px; text-align: center; color: #8A8F9E; font-size: 16px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-wrap">
        <div class="sidebar-logo">
            <i class="mdi mdi-forum"></i> ConversaAI
        </div>
        <span class="sidebar-menu-label">MENÚ PRINCIPAL</span>
        <div class="sidebar-nav">
            <a class="nav-btn" href="/"><i class="mdi mdi-view-dashboard"></i> Dashboard</a>
            <a class="nav-btn active" href="/tickets" target="_self"><i class="mdi mdi-ticket-confirmation"></i> Tickets</a>
            <a class="nav-btn" href="#"><i class="mdi mdi-cog-outline"></i> Configuración</a>
        </div>
        <div class="sidebar-footer">
            <a class="nav-btn logout-btn" href="#"><i class="mdi mdi-logout"></i> Cerrar sesión</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── FETCH DATA ─────────────────────────────────────────────────────────────
def fetch_tickets(params: dict) -> dict:
    try:
        resp = requests.get(f"{API_BASE}/tickets", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


# ── TOPBAR ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-left">
    <h1>ConversaAI</h1>
    <div class="topbar-title-sep"></div>
    <span class="topbar-subtitle">Listado de tickets</span>
  </div>
  <div class="topbar-right">
    <div class="icon-btn"><i class="mdi mdi-bell-outline"></i></div>
    <div class="profile-pill">
      <div class="profile-avatar">P</div> Pablo Diaz
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── FILTROS ────────────────────────────────────────────────────────────────
col_search, col_sentiment, col_resolution, col_language = st.columns([3, 1.5, 1.5, 1.5])

with col_search:
    busqueda = st.text_input("buscar", placeholder="🔍 Buscar por intent o ID...", label_visibility="collapsed")

with col_sentiment:
    sentiment_opts = ["Todos los sentimientos", "Positive", "Negative", "Neutral"]
    sent_filter = st.selectbox("Sentimiento", sentiment_opts, label_visibility="collapsed")

with col_resolution:
    res_opts = ["Todas las resoluciones", "SUCCESS", "FRUSTRATION", "NEUTRAL"]
    res_filter = st.selectbox("Resolución", res_opts, label_visibility="collapsed")

with col_language:
    lang_opts = ["Todos los idiomas", "es", "pt"]
    lang_filter = st.selectbox("Idioma", lang_opts, label_visibility="collapsed")


# ── BUILD QUERY ────────────────────────────────────────────────────────────
params = {"page": 1, "page_size": 30}
if sent_filter != "Todos los sentimientos":
    params["sentiment"] = sent_filter
if res_filter != "Todas las resoluciones":
    params["resolution"] = res_filter
if lang_filter != "Todos los idiomas":
    params["language"] = lang_filter

data = fetch_tickets(params)

if not data:
    st.markdown('<div class="table-wrap"><div class="no-results">⚠ No se pudo conectar con la API</div></div>', unsafe_allow_html=True)
    st.stop()

tickets = data.get("tickets", [])
total = data.get("total", 0)

# Filtro local de búsqueda
if busqueda:
    b = busqueda.lower()
    tickets = [t for t in tickets if b in t.get("intent", "").lower() or b in str(t.get("session_id", "")).lower()]


# ── SUMMARY PILLS ──────────────────────────────────────────────────────────
# Emulamos los pills de resumen (Total, Frustración, Abandono, etc)
st.markdown(f"""
<div class="tickets-summary">
    <div class="summary-pill">Total <span>{total}</span></div>
    <div class="summary-pill">Tickets filtrados <span>{len(tickets)}</span></div>
</div>
""", unsafe_allow_html=True)


# ── TABLA / LISTA ──────────────────────────────────────────────────────────
def _sentiment_cls(group: str) -> tuple[str, str, str, str]:
    if group == "Positive":
        return "Positivo", "tag-positivo", "mdi-emoticon-outline", "icon-pos"
    elif group == "Negative":
        return "Negativo", "tag-negativo", "mdi-emoticon-angry-outline", "icon-neg"
    else:
        return "Neutral", "tag-neutral", "mdi-emoticon-neutral-outline", "icon-neu"


rows_html = ""
for t in tickets:
    sent_text, sent_cls, icon, icon_cls = _sentiment_cls(t.get("sentiment_group", ""))
    
    # Resolucion
    res_raw = t.get("resolution", "")
    res_text = "Éxito" if res_raw == "SUCCESS" else "Frustración" if res_raw == "FRUSTRATION" else "Neutral"
    res_tag_cls = "tag-positivo" if res_raw == "SUCCESS" else "tag-negativo" if res_raw == "FRUSTRATION" else "tag-neutral"

    intent = t.get("intent", "—").replace("_", " ").title()
    lang = (t.get("language") or "es").upper()
    date_str = t.get("date", "")
    sid_short = str(t.get("session_id", ""))[:8]

    # Prevenir bugs de identacion en Streamlit -> Todo en una linea.
    rows_html += f'<div class="ticket-card"><div class="ticket-main"><div class="ticket-icon {icon_cls}"><i class="mdi {icon}"></i></div><div class="ticket-info"><div class="ticket-id">#{sid_short} <span class="ticket-time">• hace un rato ({date_str})</span></div><div class="ticket-intent">{intent}</div></div></div><div class="ticket-tags"><span class="tag tag-idioma">{lang}</span><span class="tag {sent_cls}">{sent_text}</span><span class="tag {res_tag_cls}">{res_text}</span><i class="mdi mdi-chevron-right" style="color:#A3A8B8;font-size:24px;margin-left:8px;"></i></div></div>'

if not tickets:
    rows_html = '<div class="no-results">No se encontraron tickets con estos filtros.</div>'

st.markdown(f'<div class="table-wrap">{rows_html}</div>', unsafe_allow_html=True)

# ── PAGINACIÓN ─────────────────────────────────────────────────────────────
st.markdown(f'<div style="padding:0 32px 32px;font-size:14px;font-weight:500;color:#8A8F9E;text-align:center;">Mostrando {len(tickets)} de {total} tickets evaluados</div>', unsafe_allow_html=True)
