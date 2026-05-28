"""
Página de Tickets — Consume datos desde la API de FastAPI.
Filtros consumen fact_tag_assignments + dim_tags (RF#12).
"""
import streamlit as st
import requests
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1/dashboard")

st.set_page_config(page_title="ConversaAI — Tickets", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

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
[data-testid="stHorizontalBlock"] { gap: 8px !important; padding: 0 24px 20px !important; align-items: center !important; }
[data-testid="column"] { padding: 0 !important; }

[data-testid="stSidebar"] { background-color: #0D19B3 !important; width: 220px !important; min-width: 220px !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; background-color: #0D19B3 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding: 0 !important; gap: 0 !important; }
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }
.sidebar-wrap { display: flex; flex-direction: column; height: 100vh; background: #0D19B3; }
[data-testid="stSidebar"] > div > div > div { padding-top: 0 !important; }
.sidebar-brand { padding: 0px 16px 12px; border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 12px; }
.sidebar-brand h2 { font-size: 16px; font-weight: 600; color: #ffffff !important; margin-bottom: 3px; margin-top: 0; }
.sidebar-brand p  { font-size: 10px; color: #C8D4FF !important; margin: 0; }
.sidebar-menu-label { font-size: 10px; font-weight: 600; letter-spacing: 0.08em; color: #ffffff !important; padding: 0 16px 8px; display: block; }
.sidebar-nav { flex: 1; padding: 0 8px; }
.nav-btn { display: flex; align-items: center; gap: 8px; padding: 10px 8px; border-radius: 8px; margin-bottom: 2px; font-size: 12px; text-decoration: none !important; color: #C8D4FF !important; }
.nav-btn i { font-size: 16px; color: #C8D4FF !important; }
.nav-btn.active { background: #2E52F5 !important; color: #ffffff !important; }
.nav-btn.active i { color: #ffffff !important; }
.sidebar-footer { border-top: 1px solid rgba(255,255,255,0.15); padding: 12px 8px; }

.topbar { background: #ffffff; display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; border-bottom: 1px solid #F0F2F8; margin-bottom: 20px; }
.topbar h1 { font-size: 18px; font-weight: 600; color: #0A1172; margin: 0; padding: 0 !important; }
.topbar p  { font-size: 10px; color: #8892A8; margin: 0; }

[data-testid="stTextInput"] { margin: 0 !important; }
[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] > div { border: none !important; box-shadow: none !important; background: transparent !important; }
[data-testid="stTextInput"] > div > div { background: #F0F2F8 !important; border: 1px solid #D0DAFF !important; border-radius: 6px !important; height: 32px !important; min-height: 32px !important; padding: 0 8px !important; box-shadow: none !important; }
[data-testid="stTextInput"] input { font-size: 12px !important; color: #8892A8 !important; font-family: 'Inter', sans-serif !important; background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; height: 32px !important; }

[data-testid="stSelectbox"] { margin: 0 !important; }
[data-testid="stSelectbox"] label { display: none !important; }
[data-testid="stSelectbox"] > div > div { background: #F0F2F8 !important; border: 1px solid #D0DAFF !important; border-radius: 6px !important; height: 32px !important; min-height: 32px !important; font-size: 12px !important; color: #8892A8 !important; font-family: 'Inter', sans-serif !important; }

.table-wrap { padding: 0 24px 24px; }
.table-card { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); overflow: hidden; }
.table-header { display: grid; grid-template-columns: 1fr 170px 110px 80px 120px; padding: 10px 16px; border-bottom: 2px solid #F0F2F8; }
.th { font-size: 11px; font-weight: 600; color: #8892A8; letter-spacing: 0.04em; text-transform: uppercase; }
.ticket-row { display: grid; grid-template-columns: 1fr 170px 110px 80px 120px; padding: 14px 16px; border-bottom: 1px solid #F0F2F8; align-items: center; border-left: 3px solid transparent; cursor: pointer; transition: background 0.1s; }
.ticket-row:last-child { border-bottom: none; }
.ticket-row:hover { background: #F8F9FC; }
.row-pos { border-left-color: #1D9E75; }
.row-neg { border-left-color: #E8593C; }
.row-neu { border-left-color: #8892A8; }
.ticket-id   { font-size: 12px; font-weight: 600; color: #1A2035; margin-bottom: 2px; }
.ticket-time { font-size: 11px; color: #8892A8; font-weight: 400; }
.tag { display: inline-block; font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 99px; }
.tag-intencion   { background: #EBF0FF; color: #2E52F5; }
.tag-positivo    { background: #D1F5E8; color: #1D9E75; }
.tag-neutral     { background: #F0F2F8; color: #8892A8; }
.tag-negativo    { background: #FDECEA; color: #E8593C; }
.tag-idioma      { background: #FFF3CC; color: #B07D00; }
.tag-frustracion { background: #FDECEA; color: #E8593C; }
.tag-exito       { background: #D1F5E8; color: #1D9E75; }
.tag-neutro-st   { background: #F0F2F8; color: #8892A8; }
.no-results { padding: 40px; text-align: center; color: #8892A8; font-size: 14px; }
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
  <div><h1>Tickets</h1><p>Sesiones evaluadas por el pipeline</p></div>
</div>
""", unsafe_allow_html=True)


# ── FILTROS ────────────────────────────────────────────────────────────────
col_search, col_sentiment, col_resolution, col_language = st.columns([3, 1.5, 1.5, 1.5])

with col_search:
    busqueda = st.text_input("buscar", placeholder="Buscar por intent...", label_visibility="collapsed")

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

# Filtro local de búsqueda
if busqueda:
    b = busqueda.lower()
    tickets = [t for t in tickets if b in t.get("intent", "").lower() or b in str(t.get("session_id", "")).lower()]


# ── TABLA ──────────────────────────────────────────────────────────────────
def _sentiment_cls(group: str) -> tuple[str, str]:
    m = {"Positive": ("Positivo", "tag-positivo"), "Negative": ("Negativo", "tag-negativo"), "Neutral": ("Neutral", "tag-neutral")}
    return m.get(group, ("—", "tag-neutral"))

def _resolution_cls(res: str) -> tuple[str, str]:
    m = {"SUCCESS": ("Éxito", "tag-exito"), "FRUSTRATION": ("Frustración", "tag-frustracion"), "NEUTRAL": ("Neutro", "tag-neutro-st")}
    return m.get(res, ("—", "tag-neutro-st"))

def _row_cls(group: str) -> str:
    return {"Positive": "row-pos", "Negative": "row-neg"}.get(group, "row-neu")


rows_html = ""
for t in tickets:
    sent_text, sent_cls = _sentiment_cls(t.get("sentiment_group", ""))
    res_text, res_cls = _resolution_cls(t.get("resolution", ""))
    row_c = _row_cls(t.get("sentiment_group", ""))
    intent = t.get("intent", "—").replace("_", " ").title()
    lang = (t.get("language") or "—").upper()
    date_str = t.get("date", "")
    sid_short = str(t.get("session_id", ""))[:8]

    rows_html += (
        f'<div class="ticket-row {row_c}">'
        f'<div><div class="ticket-id">#{sid_short} · <span class="ticket-time">{date_str}</span></div></div>'
        f'<div><span class="tag tag-intencion">{intent}</span></div>'
        f'<div><span class="tag {sent_cls}">{sent_text}</span></div>'
        f'<div><span class="tag tag-idioma">{lang}</span></div>'
        f'<div><span class="tag {res_cls}">{res_text}</span></div>'
        f'</div>'
    )

if not tickets:
    rows_html = '<div class="no-results">No se encontraron tickets con estos filtros.</div>'

st.markdown(
    '<div class="table-wrap"><div class="table-card">'
    '<div class="table-header">'
    '<div class="th">ID / Fecha</div><div class="th">Intención</div>'
    '<div class="th">Sentimiento</div><div class="th">Idioma</div>'
    '<div class="th">Resolución</div>'
    '</div>' + rows_html + '</div></div>',
    unsafe_allow_html=True
)

# ── PAGINACIÓN ─────────────────────────────────────────────────────────────
total_pages = data.get("total_pages", 1)
total = data.get("total", 0)
st.markdown(f'<div style="padding:0 24px;font-size:12px;color:#8892A8;">Mostrando {len(tickets)} de {total} tickets evaluados</div>', unsafe_allow_html=True)
