import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ConversaAI — Tickets", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

TELEGRAM_SVG = """<svg width="12" height="11" viewBox="0 0 11 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M9.48532 0.0906039C7.5813 1.1182 2.29404 3.97121 0.397196 4.99465C0.141714 5.1326 -0.0121029 5.40396 0.000746782 5.69383C0.0139744 5.98333 0.191599 6.24031 0.458041 6.35445L3.01966 7.45385L3.0072 9.06044C3.00455 9.37299 3.19502 9.65531 3.48641 9.76945C3.77742 9.88396 4.10924 9.80724 4.32051 9.5767L5.40253 8.39453L8.1603 9.30723C8.3674 9.37601 8.59454 9.35145 8.78237 9.23996C8.97058 9.12885 9.10135 8.94177 9.14103 8.72673L10.5874 0.893329C10.6403 0.607234 10.5243 0.316231 10.2892 0.14465C10.0537 -0.026553 9.74118 -0.0473412 9.48532 0.0906039ZM9.7272 1.39031L8.39764 8.58954L5.40782 7.60011C5.26647 7.55325 5.11076 7.59407 5.01023 7.70367L3.76306 9.06611L3.77628 7.36277L9.7272 1.39031ZM0.755855 5.65981L3.31294 6.75695L8.6501 1.40014L0.755855 5.65981Z" fill="#4B6BFF"/></svg>"""
TELEGRAM_SVG_W = """<svg width="12" height="11" viewBox="0 0 11 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M9.48532 0.0906039C7.5813 1.1182 2.29404 3.97121 0.397196 4.99465C0.141714 5.1326 -0.0121029 5.40396 0.000746782 5.69383C0.0139744 5.98333 0.191599 6.24031 0.458041 6.35445L3.01966 7.45385L3.0072 9.06044C3.00455 9.37299 3.19502 9.65531 3.48641 9.76945C3.77742 9.88396 4.10924 9.80724 4.32051 9.5767L5.40253 8.39453L8.1603 9.30723C8.3674 9.37601 8.59454 9.35145 8.78237 9.23996C8.97058 9.12885 9.10135 8.94177 9.14103 8.72673L10.5874 0.893329C10.6403 0.607234 10.5243 0.316231 10.2892 0.14465C10.0537 -0.026553 9.74118 -0.0473412 9.48532 0.0906039ZM9.7272 1.39031L8.39764 8.58954L5.40782 7.60011C5.26647 7.55325 5.11076 7.59407 5.01023 7.70367L3.76306 9.06611L3.77628 7.36277L9.7272 1.39031ZM0.755855 5.65981L3.31294 6.75695L8.6501 1.40014L0.755855 5.65981Z" fill="white"/></svg>"""

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

/* SIDEBAR */
[data-testid="stSidebar"] { background-color: #0D19B3 !important; width: 220px !important; min-width: 220px !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; background-color: #0D19B3 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding: 0 !important; gap: 0 !important; }
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }
.sidebar-wrap { display: flex; flex-direction: column; height: 100vh; background: #0D19B3; }
[data-testid="stSidebar"] > div > div > div { padding-top: 0 !important; } .sidebar-brand { padding: 0px 16px 12px; border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 12px; }
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
.topbar { background: #ffffff; display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; border-bottom: 1px solid #F0F2F8; margin-bottom: 20px; }
.topbar h1 { font-size: 18px; font-weight: 600; color: #0A1172; margin: 0 0 0px 0; padding: 0 !important; }
.topbar p  { font-size: 10px; color: #8892A8; margin: 0; }
.topbar-right { display: flex; align-items: center; gap: 24px; }
.topbar-date { font-size: 12px; color: #8892A8; }
.topbar-avatar { width: 36px; height: 36px; border-radius: 50%; background: #D1F5E8; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; color: #0A5C3F; }

/* FILTROS WRAPPER */
.filtros-wrap { display: flex; align-items: center; gap: 8px; padding: 0 24px 20px; }

/* SEARCH */
[data-testid="stTextInput"] { margin: 0 !important; }
[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] > div { border: none !important; box-shadow: none !important; background: transparent !important; }
[data-testid="stTextInput"] > div > div { background: #F0F2F8 !important; border: 1px solid #D0DAFF !important; border-radius: 6px !important; height: 32px !important; min-height: 32px !important; padding: 0 8px !important; box-shadow: none !important; }
[data-testid="stTextInput"] input { font-size: 12px !important; color: #8892A8 !important; font-family: 'Inter', sans-serif !important; background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; height: 32px !important; }
[data-testid="stTextInput"] > div > div:focus-within { background: #ffffff !important; border: 2px solid #2E52F5 !important; box-shadow: none !important; }
[data-testid="stTextInput"] > div > div:focus-within input { color: #1A2035 !important; }
[data-testid="stTextInput"] > div > div::before { font-family: 'Material Design Icons'; content: "\F0349"; color: #8892A8; font-size: 16px; margin-right: 4px; }

/* CHIPS */
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 0 10px; height: 32px; border-radius: 16px; font-size: 12px; font-weight: 500; cursor: pointer; font-family: 'Inter', sans-serif; transition: all 0.15s; border: none; }
.chip-todos         { background: #F0F2F8; border: 1px solid #D0DAFF; color: #1A2035; }
.chip-tg-off        { background: #ffffff; border: 1.5px solid #C8D4FF; color: #2E3A56; }
.chip-tg-off:hover  { background: #EBF0FF; border-color: #7090FF; color: #1228D4; }
.chip-tg-on         { background: #1228D4; border: 1.5px solid #0D19B3; color: #ffffff; box-shadow: 0 4px 12px rgba(18,40,212,0.3); }
.chip-wa-off        { background: #ffffff; border: 1.5px solid #C8D4FF; color: #2E3A56; }
.chip-wa-off:hover  { background: #EBF0FF; border-color: #7090FF; color: #1228D4; }
.chip-wa-on         { background: #1D9E75; border: 1.5px solid #0A5C3F; color: #ffffff; box-shadow: 0 4px 12px rgba(29,158,117,0.3); }

/* SELECTBOX */
[data-testid="stSelectbox"] { margin: 0 !important; }
[data-testid="stSelectbox"] label { display: none !important; }
[data-testid="stSelectbox"] > div > div { background: #F0F2F8 !important; border: 1px solid #D0DAFF !important; border-radius: 6px !important; height: 32px !important; min-height: 32px !important; font-size: 12px !important; color: #8892A8 !important; font-family: 'Inter', sans-serif !important; }

/* TABLA */
.table-wrap { padding: 0 24px 24px; }
.table-card { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(26,32,53,0.06); overflow: hidden; }
.table-header { display: grid; grid-template-columns: 52px 1fr 170px 110px 80px 120px; padding: 10px 16px; border-bottom: 2px solid #F0F2F8; }
.th { font-size: 11px; font-weight: 600; color: #8892A8; letter-spacing: 0.04em; text-transform: uppercase; }
.ticket-row { display: grid; grid-template-columns: 52px 1fr 170px 110px 80px 120px; padding: 14px 16px; border-bottom: 1px solid #F0F2F8; align-items: center; border-left: 3px solid transparent; cursor: pointer; transition: background 0.1s; }
.ticket-row:last-child { border-bottom: none; }
.ticket-row:hover { background: #F8F9FC; }
.row-tg { border-left-color: #4B6BFF; }
.row-wa { border-left-color: #1D9E75; }
.canal-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.canal-icon.tg { background: #EBF0FF; }
.canal-icon.wa { background: #D1F5E8; }
.ticket-id   { font-size: 12px; font-weight: 600; color: #1A2035; margin-bottom: 2px; }
.ticket-time { font-size: 11px; color: #8892A8; font-weight: 400; }
.ticket-msg  { font-size: 12px; color: #8892A8; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 380px; }
.tag { display: inline-block; font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 99px; }
.tag-intencion   { background: #EBF0FF; color: #2E52F5; }
.tag-positivo    { background: #D1F5E8; color: #1D9E75; }
.tag-neutral     { background: #F0F2F8; color: #8892A8; }
.tag-negativo    { background: #FDECEA; color: #E8593C; }
.tag-idioma      { background: #FFF3CC; color: #B07D00; }
.tag-frustracion { background: #FDECEA; color: #E8593C; }
.tag-exito       { background: #D1F5E8; color: #1D9E75; }
.tag-neutro-st   { background: #F0F2F8; color: #8892A8; }
.tag-en-curso    { background: #EBF0FF; color: #2E52F5; }
.tag-reclamo     { background: #FDECEA; color: #E8593C; }
.tag-agradec     { background: #D1F5E8; color: #1D9E75; }
.tag-confirm     { background: #D1F5E8; color: #1D9E75; }
.tag-cancel      { background: #FDECEA; color: #E8593C; }
.no-results { padding: 40px; text-align: center; color: #8892A8; font-size: 14px; }

/* Botones canal */
.chip-todos-off button, .chip-todos-on button,
.chip-tg-off button, .chip-tg-on button,
.chip-wa-off button, .chip-wa-on button {
    height: 32px !important; padding: 0 12px !important;
    border-radius: 16px !important; font-size: 12px !important;
    font-weight: 500 !important; font-family: 'Inter', sans-serif !important;
    white-space: nowrap !important; transition: all 0.15s !important; box-shadow: none !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
.chip-todos-off button { background: #F0F2F8 !important; border: 1px solid #D0DAFF !important; color: #1A2035 !important; }
.chip-todos-on button  { background: #EBF0FF !important; border: 1px solid #A0B4FF !important; color: #1228D4 !important; }
.chip-tg-off button    { background: #ffffff !important; border: 1.5px solid #C8D4FF !important; color: #2E3A56 !important; }
.chip-tg-off button:hover { background: #EBF0FF !important; border-color: #7090FF !important; color: #1228D4 !important; }
.chip-tg-on button     { background: #1228D4 !important; border: 1.5px solid #0D19B3 !important; color: #ffffff !important; box-shadow: 0 4px 12px rgba(18,40,212,0.3) !important; }
.chip-wa-off button    { background: #ffffff !important; border: 1.5px solid #C8D4FF !important; color: #2E3A56 !important; }
.chip-wa-off button:hover { background: #EBF0FF !important; border-color: #7090FF !important; color: #1228D4 !important; }
.chip-wa-on button     { background: #1D9E75 !important; border: 1.5px solid #0A5C3F !important; color: #ffffff !important; box-shadow: 0 4px 12px rgba(29,158,117,0.3) !important; }

/* Quitar gap entre columnas de chips */
.chip-cols [data-testid="stHorizontalBlock"] { gap: 6px !important; padding: 0 !important; }
.chip-cols [data-testid="column"] { flex: 0 0 auto !important; width: auto !important; }
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
st.markdown("""
<div class="topbar">
  <div><h1>Tickets</h1><p>247 conversaciones recibidas</p></div>
  <div class="topbar-right">
    <span class="topbar-date">14 May 2026</span>
    <div class="topbar-avatar">P</div>
  </div>
</div>
""", unsafe_allow_html=True)

# DATOS
TICKETS = [
    {"canal":"tg","id":"#0247","time":"hace 3 min",   "msg":"No me aparece el estado de mi pedido, ya probé tres veces y sigue si...","intencion":"Consulta de estado","tono":"Negativo","idioma":"Es","estado":"Frustración","i_cls":"tag-intencion","t_cls":"tag-negativo","e_cls":"tag-frustracion"},
    {"canal":"wa","id":"#0246","time":"hace 8 min",   "msg":"Quiero hablar con una persona, el bot no me entiende bien y necesito...","intencion":"Solicitar operador","tono":"Negativo","idioma":"Es","estado":"Frustración","i_cls":"tag-intencion","t_cls":"tag-negativo","e_cls":"tag-frustracion"},
    {"canal":"tg","id":"#0245","time":"hace 15 min",  "msg":"Joyita, gracias! me ayudó mucho la información que me diste sobre el...","intencion":"Agradecimiento",   "tono":"Positivo","idioma":"Es","estado":"Éxito",      "i_cls":"tag-agradec", "t_cls":"tag-positivo","e_cls":"tag-exito"},
    {"canal":"wa","id":"#0244","time":"hace 22 min",  "msg":"Bom dia, preciso de ajuda com meu pedido que chegou errado ontem à t...","intencion":"Reclamo",          "tono":"Negativo","idioma":"Pt","estado":"En curso",  "i_cls":"tag-reclamo", "t_cls":"tag-negativo","e_cls":"tag-en-curso"},
    {"canal":"tg","id":"#0243","time":"hace 32 min",  "msg":"Ok gracias por la info, ya entendí el proceso, lo reviso después",      "intencion":"Confirmación",     "tono":"Neutral", "idioma":"Es","estado":"Neutro",    "i_cls":"tag-confirm", "t_cls":"tag-neutral", "e_cls":"tag-neutro-st"},
    {"canal":"wa","id":"#0242","time":"hace 45 min",  "msg":"Preciso cancelar meu pedido número 9921, é urgente por favor respond...","intencion":"Cancelación",      "tono":"Negativo","idioma":"Pt","estado":"Frustración","i_cls":"tag-cancel",  "t_cls":"tag-negativo","e_cls":"tag-frustracion"},
    {"canal":"tg","id":"#0241","time":"hace 1h",      "msg":"Hola, cuánto tarda el envío a Córdoba Capital? necesito saber si lle...","intencion":"Consulta de estado","tono":"Neutral","idioma":"Es","estado":"En curso",  "i_cls":"tag-intencion","t_cls":"tag-neutral","e_cls":"tag-en-curso"},
    {"canal":"wa","id":"#0240","time":"hace 1h 10min","msg":"Muito obrigado pela ajuda! Resolveu meu problema rapidamente, excele...","intencion":"Agradecimiento",   "tono":"Positivo","idioma":"Pt","estado":"Éxito",      "i_cls":"tag-agradec", "t_cls":"tag-positivo","e_cls":"tag-exito"},
]

# SESSION STATE
if "canal_filtro" not in st.session_state:
    st.session_state.canal_filtro = "Todos"

canal = st.session_state.canal_filtro

# FILTROS — search y selectboxes en columnas, chips en HTML dentro de una columna
col_search, col_chips, col_tono, col_estado, col_idioma = st.columns([2.4, 2.6, 1.4, 1.4, 1.4])

with col_search:
    busqueda = st.text_input("buscar", placeholder="Buscar ticket o mensaje...", label_visibility="collapsed")

with col_chips:
    st.markdown('<div class="chip-cols">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="{"chip-todos-on" if canal=="Todos" else "chip-todos-off"}">', unsafe_allow_html=True)
        if st.button("Todos", key="btn_todos"):
            st.session_state.canal_filtro = "Todos"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="{"chip-tg-on" if canal=="tg" else "chip-tg-off"}">', unsafe_allow_html=True)
        if st.button("✈ Telegram", key="btn_tg"):
            st.session_state.canal_filtro = "tg"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="{"chip-wa-on" if canal=="wa" else "chip-wa-off"}">', unsafe_allow_html=True)
        if st.button("● WhatsApp", key="btn_wa"):
            st.session_state.canal_filtro = "wa"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_tono:
    tono_filtro = st.selectbox("Tono", ["Filtro por tono", "Positivo", "Neutral", "Negativo"], label_visibility="collapsed")

with col_estado:
    estado_filtro = st.selectbox("Estado", ["Filtro por estado", "Frustración", "Éxito", "Neutro", "En curso"], label_visibility="collapsed")

with col_idioma:
    idioma_filtro = st.selectbox("Idioma", ["Filtro por idioma", "Español", "Portugués"], label_visibility="collapsed")

# APLICAR FILTROS
filtrados = TICKETS[:]
if st.session_state.canal_filtro != "Todos":
    filtrados = [t for t in filtrados if t["canal"] == st.session_state.canal_filtro]
if busqueda:
    b = busqueda.lower()
    filtrados = [t for t in filtrados if b in t["id"].lower() or b in t["msg"].lower()]
if tono_filtro != "Filtro por tono":
    filtrados = [t for t in filtrados if t["tono"] == tono_filtro]
if estado_filtro != "Filtro por estado":
    filtrados = [t for t in filtrados if t["estado"] == estado_filtro]
if idioma_filtro != "Filtro por idioma":
    idioma_map = {"Español": "Es", "Portugués": "Pt"}
    filtrados = [t for t in filtrados if t["idioma"] == idioma_map[idioma_filtro]]

# TABLA
rows_html = ""
for t in filtrados:
    row_cls = "row-tg" if t["canal"] == "tg" else "row-wa"
    icon = f'<div class="canal-icon tg">{TELEGRAM_SVG}</div>' if t["canal"] == "tg" else '<div class="canal-icon wa"><i class="mdi mdi-whatsapp" style="color:#1D9E75;font-size:15px;"></i></div>'
    rows_html += (
        f'<div class="ticket-row {row_cls}">'
        f'<div>{icon}</div>'
        f'<div><div class="ticket-id">{t["id"]} · <span class="ticket-time">{t["time"]}</span></div>'
        f'<div class="ticket-msg">{t["msg"]}</div></div>'
        f'<div><span class="tag {t["i_cls"]}">{t["intencion"]}</span></div>'
        f'<div><span class="tag {t["t_cls"]}">{t["tono"]}</span></div>'
        f'<div><span class="tag tag-idioma">{t["idioma"]}</span></div>'
        f'<div><span class="tag {t["e_cls"]}">{t["estado"]}</span></div>'
        f'</div>'
    )

if not filtrados:
    rows_html = '<div class="no-results">No se encontraron tickets con estos filtros.</div>'

st.markdown(
    '<div class="table-wrap"><div class="table-card">'
    '<div class="table-header">'
    '<div class="th">Canal</div><div class="th">ID</div>'
    '<div class="th">Intención</div><div class="th">Tono</div>'
    '<div class="th">Idioma</div><div class="th">Estado</div>'
    '</div>' + rows_html + '</div></div>',
    unsafe_allow_html=True
)
