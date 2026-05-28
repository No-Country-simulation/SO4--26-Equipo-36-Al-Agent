"""
Página de Tickets — Consume datos desde la API de FastAPI.
Dark Mode premium, sin tags HTML abiertos que rompan el layout nativo de Streamlit.
"""
import streamlit as st
import requests
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1/dashboard")

st.set_page_config(page_title="ConversaAI — Tickets", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = None

def set_ticket(sid):
    st.session_state.selected_ticket = sid

def clear_ticket():
    st.session_state.selected_ticket = None

from layout import load_global_css, render_sidebar, render_topbar

# ── ESTILOS GLOBALES Y COMPONENTES UI ──────────────────────────────────────
load_global_css()

st.markdown("""
<style>
/* ── SEARCH & FILTERS ── */
[data-testid="stTextInput"] { margin: 0 !important; height: 48px !important; }
[data-testid="stTextInput"] > div { height: 48px !important; overflow: visible !important; }
[data-testid="stTextInput"] div[data-baseweb="input"] { 
    background-color: transparent !important; 
    border: none !important; 
    height: 48px !important; 
    overflow: visible !important; 
}
[data-testid="stTextInput"] div[data-baseweb="base-input"] { 
    background-color: #1A1D24 !important; 
    border: 1px solid rgba(255,255,255,0.05) !important; 
    border-radius: 99px !important; 
    height: 48px !important;
    min-height: 48px !important; 
    max-height: 48px !important;
    padding: 0 24px !important; 
    display: flex;
    align-items: center;
    box-sizing: border-box !important;
    overflow: visible !important;
}
/* Icono lupa (magnify) */
[data-testid="stTextInput"] div[data-baseweb="base-input"]::before {
    content: "\\F0349";
    font-family: "Material Design Icons";
    font-size: 20px;
    color: #8A8F9E;
    margin-right: 8px;
}
[data-testid="stTextInput"] input { 
    font-size: 14px !important; 
    color: #F2F4F7 !important; 
    background: transparent !important; 
    border: none !important; 
    box-shadow: none !important; 
    padding: 0 !important;
    margin: 0 !important;
    height: 100% !important;
    line-height: normal !important;
    -webkit-text-fill-color: #F2F4F7 !important;
}

/* Filter Popover Button */
[data-testid="stPopover"] { display: block !important; }
[data-testid="stPopover"] button {
    background-color: #1A1D24 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 99px !important;
    height: 48px !important;
    min-height: 48px !important;
    max-height: 48px !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 16px !important;
    box-sizing: border-box !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stPopover"] button:hover { background-color: #282C38 !important; }
[data-testid="stPopover"] button p {
    color: #F2F4F7 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
    white-space: nowrap !important;
}
/* Injecting Funnel Icon */
[data-testid="stPopover"] button p::before {
    content: "\\F0236";
    font-family: "Material Design Icons";
    margin-right: 8px;
    font-size: 18px;
    color: #A3A8B8;
}

/* Filter Popover Body & Portals */
div[data-baseweb="popover"] > div {
    background-color: #1A1D24 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    outline: none !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important;
    border-radius: 16px !important;
}
div[data-baseweb="popover"] > div:focus, div[data-baseweb="popover"] > div:focus-visible {
    outline: none !important; border: none !important;
}
[data-testid="stPopoverBody"] { 
    background-color: transparent !important; 
    border: none !important;
    outline: none !important;
    width: max-content !important;
    min-width: 240px !important;
    max-height: 800px !important;
    padding: 20px !important;
    overflow-x: hidden !important;
}

/* Radio Buttons Fix */
[data-testid="stRadio"] * { color: #F2F4F7 !important; font-size: 14px !important; }
[data-testid="stRadio"] label { color: #F2F4F7 !important; }

/* Multiselect Input Fix */
div[data-baseweb="select"] > div { 
    background-color: #282C38 !important; 
    border: 1px solid rgba(255,255,255,0.05) !important; 
    border-radius: 8px !important;
}
div[data-baseweb="select"] * { color: #F2F4F7 !important; }
div[data-baseweb="select"] [aria-placeholder] { color: #8A8F9E !important; }
span[data-baseweb="tag"] { 
    background-color: #1A1D24 !important; 
    border: 1px solid rgba(255,255,255,0.1) !important; 
}
span[data-baseweb="tag"] * { color: #F2F4F7 !important; }

/* Multiselect Dropdown Portal Fix (Aggressive with :has) */
div[data-baseweb="popover"] > div:has([role="listbox"]) {
    background-color: #282C38 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
[role="listbox"] {
    background-color: transparent !important;
    outline: none !important;
    padding: 4px !important;
}
[role="option"] {
    background-color: transparent !important;
    color: #F2F4F7 !important;
    border-radius: 6px !important;
    padding: 10px 14px !important;
    margin-bottom: 2px !important;
}
[role="option"]:hover, [role="option"][aria-selected="true"] {
    background-color: rgba(208,237,87,0.15) !important;
    color: #D0ED57 !important;
}

[data-testid="stDateInput"] input {
    color: #F2F4F7 !important;
    background-color: #282C38 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}

/* ── TICKETS LIST ── */
.tickets-summary { display: flex; gap: 12px; margin-bottom: 24px; margin-top: 32px; }
.summary-pill { font-size: 14px; font-weight: 500; color: #A3A8B8; background: #282C38; padding: 8px 16px; border-radius: 99px; display: flex; gap: 6px; align-items: center; border: 1px solid rgba(255,255,255,0.05); }
.summary-pill span { font-weight: 700; color: #F2F4F7; }

.ticket-row-container { margin-bottom: 12px; background: #1A1D24; border-radius: 16px; display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; border: 1px solid rgba(255,255,255,0.02); transition: 0.2s; }
.ticket-row-container:hover { background: #282C38; }
.ticket-main { display: flex; align-items: center; gap: 16px; flex: 1; }
.ticket-icon { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; background: #282C38; color: #8A8F9E; border: 1px solid rgba(255,255,255,0.05); }
.ticket-info { display: flex; flex-direction: column; gap: 2px; }
.ticket-id { font-size: 14px; font-weight: 700; color: #F2F4F7; display: flex; align-items: center; gap: 6px; }
.ticket-time { font-size: 13px; font-weight: 400; color: #8A8F9E; }
.ticket-intent { font-size: 14px; color: #A3A8B8; }

/* Chevron Button */
.stButton button { 
    background: transparent !important; border: none !important; color: #8A8F9E !important; 
    box-shadow: none !important; width: 40px !important; height: 40px !important; padding: 0 !important;
    border-radius: 50% !important; display: flex; align-items: center; justify-content: center; font-size: 24px !important;
}
.stButton button:hover { background: rgba(255,255,255,0.05) !important; color: #F2F4F7 !important; }

/* ── TICKET DETAIL ── */
.detail-breadcrumb-card { background: #1A1D24; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.02); }
.breadcrumb { font-size: 18px; font-weight: 400; color: #F2F4F7; }
.badge-frustration { background: rgba(233,115,88,0.15); color: #E97358; padding: 6px 16px; border-radius: 99px; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; border: 1px solid rgba(233,115,88,0.2); }

.card { background: #1A1D24; border-radius: 16px; padding: 24px; border: 1px solid rgba(255,255,255,0.02); height: 100%; }
.card-title { font-size: 18px; font-weight: 500; color: #F2F4F7; margin-bottom: 20px; }

.data-row { padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.data-row:last-child { border-bottom: none; padding-bottom: 0; }
.data-label { font-size: 14px; font-weight: 400; color: #8A8F9E; margin-bottom: 4px; }
.data-value { font-size: 14px; font-weight: 600; color: #F2F4F7; }

.insight-card { background: rgba(208,237,87,0.05); border: 1px solid rgba(208,237,87,0.2); border-radius: 12px; padding: 16px; margin-top: 16px; }
.insight-header { display: flex; align-items: center; gap: 8px; color: #D0ED57; font-weight: 600; font-size: 14px; margin-bottom: 8px; }
.insight-text { font-size: 13px; color: #A3A8B8; line-height: 1.5; }

/* Chat */
.chat-header { font-size: 16px; font-weight: 600; color: #F2F4F7; margin-bottom: 24px; display: flex; flex-direction: column; gap: 4px;}
.chat-meta { font-size: 13px; font-weight: 400; color: #8A8F9E; }
.chat-container { display: flex; flex-direction: column; gap: 16px; }
.bubble-row { display: flex; width: 100%; margin-bottom: 8px; }
.bubble-row.user { justify-content: flex-start; }
.bubble-row.bot { justify-content: flex-end; }
.bubble { max-width: 80%; padding: 12px 20px; border-radius: 16px; font-size: 14px; line-height: 1.5; }
.bubble.user { background: #282C38; color: #F2F4F7; border-bottom-left-radius: 4px; border: 1px solid rgba(255,255,255,0.05); }
.bubble.bot { background: rgba(208,237,87,0.15); color: #D0ED57; border-bottom-right-radius: 4px; }
.bubble-time { font-size: 11px; color: #8A8F9E; margin-top: 4px; }
.bubble-row.bot .bubble-time { text-align: right; }

.alert-box { margin-top: 24px; padding: 16px; border-radius: 12px; background: rgba(233,115,88,0.1); border: 1px solid rgba(233,115,88,0.3); display: flex; gap: 12px; align-items: flex-start; }
.alert-icon { font-size: 20px; color: #E97358; }
.alert-text { font-size: 13px; color: #F2F4F7; font-weight: 500; line-height: 1.5; }

.gradient-bar-container { margin-top: 24px; background: #282C38; border-radius: 12px; padding: 16px; border: 1px solid rgba(255,255,255,0.02); }
.gradient-label { font-size: 13px; font-weight: 500; color: #8A8F9E; margin-bottom: 12px; }
.gradient-bar { height: 8px; border-radius: 99px; background: linear-gradient(90deg, #A3A8B8 0%, #D0ED57 30%, #F4A261 70%, #E97358 100%); width: 100%; position: relative; }
.gradient-labels { display: flex; justify-content: space-between; margin-top: 8px; font-size: 11px; color: #8A8F9E; font-weight: 400; }

.btn-back-wrap { margin-bottom: 16px; }
.btn-back-wrap button { width: auto !important; height: auto !important; padding: 8px 16px !important; border-radius: 8px !important; background: #1A1D24 !important; color: #F2F4F7 !important; font-size: 14px !important; font-weight: 500 !important; border: 1px solid rgba(255,255,255,0.05) !important; }
.btn-back-wrap button:hover { background: #282C38 !important; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────
render_sidebar(active_page="tickets")

# ── FETCH DATA ─────────────────────────────────────────────────────────────
def fetch_tickets(params: dict) -> dict:
    try:
        resp = requests.get(f"{API_BASE}/tickets", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

def fetch_ticket_detail(session_id: str) -> dict:
    try:
        resp = requests.get(f"{API_BASE}/tickets/{session_id}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

# ── MAIN VIEW CONTROL ───────────────────────────────────────────────────────
if st.session_state.selected_ticket is None:
    # ── VISTA 1: LISTADO ──
    render_topbar(subtitle="Listado de tickets")

    col_search, col_filter, _ = st.columns([4, 2.5, 5.5])

    with col_search:
        busqueda = st.text_input("buscar", placeholder="Buscar ticket...", label_visibility="collapsed")
    with col_filter:
        try:
            with st.popover("Filtros", use_container_width=True):
                st.markdown("<div style='font-weight:500; font-size:14px; margin-top:4px; color:#8A8F9E;'>Resolución</div>", unsafe_allow_html=True)
                res_opts = ["Todas", "SUCCESS", "NEUTRAL", "FRUSTRATION", "ABANDONED"]
                res_filter = st.radio("Resolución", res_opts, label_visibility="collapsed")
                
                st.markdown("<div style='font-weight:500; font-size:14px; margin-top:12px; color:#8A8F9E;'>Idioma</div>", unsafe_allow_html=True)
                lang_opts = ["Todos", "es", "pt", "en"]
                lang_filter = st.radio("Idioma", lang_opts, label_visibility="collapsed")
                
                st.markdown("<div style='font-weight:500; font-size:14px; margin-top:12px; color:#8A8F9E;'>Sentimiento</div>", unsafe_allow_html=True)
                sentiment_opts = ["Todos", "Positive", "Neutral", "Negative"]
                sent_filter = st.radio("Sentimiento", sentiment_opts, label_visibility="collapsed")
                
                st.markdown("<div style='font-weight:500; font-size:14px; margin-top:12px; color:#8A8F9E;'>Tags</div>", unsafe_allow_html=True)
                tag_opts = ["VIP", "Urgente", "Devolución", "Soporte", "Queja"]
                tags_filter = st.multiselect("Tags", tag_opts, label_visibility="collapsed")
                
        except AttributeError:
            with st.expander("Filtros"):
                res_opts = ["Todas", "SUCCESS", "NEUTRAL", "FRUSTRATION", "ABANDONED"]
                res_filter = st.radio("Resolución", res_opts)
                lang_opts = ["Todos", "es", "pt", "en"]
                lang_filter = st.radio("Idioma", lang_opts)
                sentiment_opts = ["Todos", "Positive", "Neutral", "Negative"]
                sent_filter = st.radio("Sentimiento", sentiment_opts)
                tag_opts = ["VIP", "Urgente", "Devolución", "Soporte", "Queja"]
                tags_filter = st.multiselect("Tags", tag_opts)

    params = {"page": 1, "page_size": 100}
    
    # ── LLAMADA API ──
    data = fetch_tickets(params)

    if not data:
        st.error("⚠ No se pudo conectar con la API")
        st.stop()

    tickets = data.get("tickets", [])
    
    # ── FILTRADO LOCAL EN TIEMPO REAL ──
    if busqueda:
        b = busqueda.lower()
        tickets = [t for t in tickets if b in str(t.get("intent", "")).lower() or b in str(t.get("session_id", "")).lower()]

    if res_filter != "Todas":
        tickets = [t for t in tickets if str(t.get("resolution", "")) == res_filter]
        
    if lang_filter != "Todos":
        tickets = [t for t in tickets if str(t.get("language", "es")).lower() == lang_filter.lower()]
        
    if sent_filter != "Todos":
        # Manejo simple: a veces el API no trae sentiment, usamos get
        tickets = [t for t in tickets if str(t.get("sentiment", "Neutral")).lower() == sent_filter.lower()]
        
    if tags_filter:
        # Si el API no provee tags por defecto, usamos un mock de lista vacía
        tickets = [t for t in tickets if any(tag in t.get("tags", []) for tag in tags_filter)]

    total = len(tickets)
    frust = len([t for t in tickets if t.get("resolution") == "FRUSTRATION"])
    aban = len([t for t in tickets if t.get("resolution") == "ABANDONED"])
    exit = len([t for t in tickets if t.get("resolution") == "SUCCESS"])
    neutral = len([t for t in tickets if t.get("resolution") == "NEUTRAL"])

    st.markdown(f"""
    <div class="px">
        <div class="tickets-summary">
            <div class="summary-pill">Total <span>{total}</span></div>
            <div class="summary-pill">Éxito <span>{exit}</span></div>
            <div class="summary-pill">Neutral <span>{neutral}</span></div>
            <div class="summary-pill">Frustración <span>{frust}</span></div>
            <div class="summary-pill">Abandono <span>{aban}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not tickets:
        st.info("No se encontraron tickets.")
    else:
        for t in tickets:
            sid = str(t.get("session_id", ""))
            sid_short = sid[:4]
            date_str = t.get("date", "hace un momento")
            intent = t.get("intent", "Sin clasificar").replace("_", " ").capitalize()
            res = t.get("resolution", "")
            icon = "mdi-message-text-outline"
            
            c_card, c_btn = st.columns([11, 1])
            with c_card:
                st.markdown(f"""
                <div class="ticket-row-container">
                    <div class="ticket-main">
                        <div class="ticket-icon"><i class="mdi {icon}"></i></div>
                        <div class="ticket-info">
                            <div class="ticket-id">#{sid_short} <span class="ticket-time">• {date_str}</span></div>
                            <div class="ticket-intent">{intent}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c_btn:
                st.button("›", key=f"btn_{sid}", on_click=set_ticket, args=(sid,))

else:
    # ── VISTA 2: DETALLE DEL TICKET ──
    sid = st.session_state.selected_ticket
    sid_short = sid[:4]
    
    render_topbar(subtitle=f"Chat de ticket #{sid_short}")

    t_data = fetch_ticket_detail(sid)
    
    st.markdown('<div class="btn-back-wrap">', unsafe_allow_html=True)
    st.button("← Volver a lista", on_click=clear_ticket, key="btn_back")
    st.markdown('</div>', unsafe_allow_html=True)

    if not t_data:
        st.error("No se pudo cargar el detalle del ticket.")
    else:
        an = t_data.get("analysis", {})
        resolution = an.get("resolution", "")
        
        badge_html = ""
        if resolution == "FRUSTRATION":
            badge_html = '<div class="badge-frustration"><i class="mdi mdi-alert-outline"></i> Frustración detectada</div>'
            
        st.markdown(f"""
            <div class="detail-breadcrumb-card">
                <div class="breadcrumb">Tickets / #{sid_short}</div>
                {badge_html}
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 2.5], gap="large")

        with col_left:
            st.markdown("""<div class="card">
            <div class="card-title">Datos del ticket</div>""", unsafe_allow_html=True)
            
            datos = [
                ("Clasificación", an.get("resolution", "Desconocido").capitalize()),
                ("Mensajes totales", f"{an.get('total_messages', 0)} mensajes"),
                ("Duración", f"{int(an.get('duration_seconds', 0)/60)} minutos"),
                ("Canal", "Telegram"),
                ("Idioma", an.get("language_name", "Español")),
                ("Último nodo", "No_match x3"),
                ("Feedback explícito", "Sin feedback")
            ]
            
            for label, val in datos:
                st.markdown(f"""
                <div class="data-row">
                    <div class="data-label">{label}</div>
                    <div class="data-value">{val}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-header"><i class="mdi mdi-auto-fix"></i> Insight de la IA</div>
                <div class="insight-text">
                    El usuario repitió la consulta de estado 3 veces sin resolución.<br>
                    Patrón de loop detectado en nodo "no_match".<br>
                    Recomendación: revisar el flujo de búsqueda por número de pedido.
                </div>
            </div>
            </div>""", unsafe_allow_html=True)

        with col_right:
            date_fmt = an.get("date", "Reciente")
            st.markdown(f"""
            <div class="card">
                <div class="chat-header">
                    Ticket #{sid_short} — Telegram · Es
                    <span class="chat-meta">Sesión: {date_fmt} · {an.get("total_messages", 0)} mensajes</span>
                </div>
                <div class="chat-container">
            """, unsafe_allow_html=True)
            
            messages = t_data.get("messages", [])
            for m in messages:
                role = m.get("role", "user")
                cls_role = "user" if role == "user" else "bot"
                sender_name = "Usuario" if role == "user" else "Bot"
                
                st.markdown(f"""
                <div class="bubble-row {cls_role}">
                    <div>
                        <div class="bubble {cls_role}">{m.get('content', '')}</div>
                        <div class="bubble-time">{sender_name} - {m.get('time', '')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

            if resolution == "FRUSTRATION":
                st.markdown("""
                <div class="alert-box">
                    <div class="alert-icon"><i class="mdi mdi-alert-outline"></i></div>
                    <div class="alert-text"><b>Clasificado como Frustración:</b> último sentimiento negativo + loop de "no encontré" >2 veces + timeout.<br>Ver RF#10 y RF#11 del ERS.</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="gradient-bar-container">
                    <div class="gradient-label">Pendiente emocional de la sesión</div>
                    <div class="gradient-bar"></div>
                    <div class="gradient-labels">
                        <span>Neutral al inicio</span>
                        <span>Frustración al cierre</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
