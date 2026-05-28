"""
Página de Tickets — Consume datos desde la API de FastAPI.
Dark Mode premium, sin tags HTML abiertos que rompan el layout nativo de Streamlit.
"""
import streamlit as st
import requests
import os
from streamlit_autorefresh import st_autorefresh

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1/dashboard")

st.set_page_config(page_title="ConversaAI — Tickets", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = None
if "last_ticket_ids" not in st.session_state:
    st.session_state.last_ticket_ids = set()
if "new_ticket_ids" not in st.session_state:
    st.session_state.new_ticket_ids = set()
if "has_notifications" not in st.session_state:
    st.session_state.has_notifications = False

def set_ticket(sid):
    st.session_state.selected_ticket = sid
    if sid in st.session_state.new_ticket_ids:
        st.session_state.new_ticket_ids.remove(sid)
    if not st.session_state.new_ticket_ids:
        st.session_state.has_notifications = False

def clear_ticket():
    st.session_state.selected_ticket = None

from layout import load_global_css, render_sidebar, render_topbar

# ── LOS ESTILOS GLOBALES FUERON MOVIDOS AL FINAL PARA EVITAR ESPACIOS FANTASMAS ──


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
    render_topbar(subtitle="Listado de tickets", has_notifications=st.session_state.has_notifications)

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

    st_autorefresh(interval=10000, key="tickets_refresh")

    params = {"page": 1, "page_size": 100}
    
    # ── LLAMADA API ──
    data = fetch_tickets(params)

    if not data:
        st.error("⚠ No se pudo conectar con la API")
        st.stop()

    tickets = data.get("tickets", [])
    
    # Ordenar por fecha descendente o session_id
    tickets = sorted(tickets, key=lambda t: t.get("created_at", t.get("date", t.get("session_id", ""))), reverse=True)

    # ── DETECCIÓN DE TICKETS NUEVOS ──
    current_ids = set(t.get("session_id") for t in tickets)
    if st.session_state.last_ticket_ids:
        new_ids = current_ids - st.session_state.last_ticket_ids
        if new_ids:
            st.session_state.new_ticket_ids.update(new_ids)
            st.toast("¡Nuevos tickets recibidos!", icon="🔔")
            st.session_state.has_notifications = True
    
    st.session_state.last_ticket_ids = current_ids

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
        # Deduplicar tickets por session_id para evitar StreamlitDuplicateElementKey
        seen_sids = set()
        unique_tickets = []
        for t in tickets:
            s_id = str(t.get("session_id", ""))
            if s_id not in seen_sids:
                seen_sids.add(s_id)
                unique_tickets.append(t)
                
        for t in unique_tickets:
            sid = str(t.get("session_id", ""))
            sid_short = sid[:4]
            date_str = t.get("date", "hace un momento")
            intent = t.get("intent", "Sin clasificar").replace("_", " ").capitalize()
            res = t.get("resolution", "")
            icon = "mdi-message-text-outline"
            is_new = sid in st.session_state.new_ticket_ids
            badge_html = '<span class="ticket-new-badge">NUEVO</span>' if is_new else ""
            card_class = "ticket-card is-new" if is_new else "ticket-card"
            
            c_card, c_btn = st.columns([11, 1])
            with c_card:
                st.markdown(f"""
                <div class="{card_class} ticket-row-container">
                    <div class="ticket-main">
                        <div class="ticket-icon"><i class="mdi {icon}"></i></div>
                        <div class="ticket-info">
                            <div class="ticket-id">#{sid_short} {badge_html} <span class="ticket-time">• {date_str}</span></div>
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
    
    render_topbar(subtitle=f"Chat de ticket #{sid_short}", has_notifications=st.session_state.has_notifications)

    t_data = fetch_ticket_detail(sid)
    
    if not t_data:
        st.button("← Volver a lista", on_click=clear_ticket, key="btn_back_error")
        st.error("No se pudo cargar el detalle del ticket.")
    else:
        an = t_data.get("analysis", {})
        resolution = an.get("resolution", "")
        
        # Removed detail-breadcrumb-card
        col_left, col_right = st.columns([1, 2.5], gap="large")

        with col_left:
            st.button("← Volver a lista", on_click=clear_ticket, key="btn_back")
            st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
            
            date_fmt = an.get("date", "Reciente")
            session_meta = f"Sesión: {date_fmt} · {an.get('total_messages', 0)} mensajes"
            card_html = f"""<div class="card">
<div class="card-title" style="margin-bottom: 4px;">Datos del ticket</div>
<div style="font-size: 13px; color: #8A8F9E; margin-bottom: 24px;">{session_meta}</div>"""
            
            tags = t_data.get("tags", [])
            tags_html = " ".join([f'<span class="ticket-new-badge">{tag.get("name", "")}</span>' for tag in tags]) if tags else "Sin tags"
            
            pos = an.get("positive_feedback", 0)
            neg = an.get("negative_feedback", 0)
            stars_text = "⭐⭐⭐⭐⭐" if pos > neg else ("⭐" if neg > pos else "⭐⭐⭐")
            
            score = an.get("sentiment_score", 0)
            slope = "Estable" if -0.3 < score < 0.3 else ("Descendente 📉" if score <= -0.3 else "Ascendente 📈")

            datos = [
                ("Clasificación", an.get("resolution", "Desconocido").capitalize()),
                ("Sentimiento", f"{an.get('sentiment_group', 'Neutral')} ({score})"),
                ("Pendiente emocional", slope),
                ("Tags", tags_html),
                ("Idioma", an.get("language_name", "Español")),
                ("Último nodo", "No_match"),
                ("Mensajes totales", f"{an.get('total_messages', 0)} mensajes"),
                ("Duración", f"{int(an.get('duration_seconds', 0)/60)} minutos"),
                ("Feedback final", stars_text)
            ]
            
            for label, val in datos:
                card_html += f"""<div class="data-row">
<div class="data-label">{label}</div>
<div class="data-value">{val}</div>
</div>"""
            
            card_html += "</div>"
            st.markdown(card_html, unsafe_allow_html=True)

        with col_right:
            chat_html = """<div class="card">
<div class="chat-container">"""
            
            messages = t_data.get("messages", [])
            for m in messages:
                role = m.get("role", "user")
                cls_role = "user" if role == "user" else "bot"
                sender_name = "Usuario" if role == "user" else "Bot"
                
                fb = m.get("feedback")
                fb_html = ""
                if fb == "positive":
                    fb_html = '<span style="color:#D0ED57; margin-left:6px;"><i class="mdi mdi-thumb-up"></i></span>'
                elif fb == "negative":
                    fb_html = '<span style="color:#E97358; margin-left:6px;"><i class="mdi mdi-thumb-down"></i></span>'
                else:
                    fb_html = '<span style="color:#62687A; margin-left:6px; font-style:italic;">(Sin feedback)</span>'
                
                chat_html += f"""<div class="bubble-row {cls_role}">
<div>
<div class="bubble {cls_role}">{m.get('content', '')}</div>
<div class="bubble-time">{sender_name} · {m.get('time', '')} {fb_html}</div>
</div>
</div>"""
            
            chat_html += "</div></div>"
            st.markdown(chat_html, unsafe_allow_html=True)

# ── ESTILOS GLOBALES AL FINAL PARA EVITAR ESPACIOS FANTASMAS ──
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

/* Volver a lista Button (Default stButton style) */
.stButton button { 
    width: max-content !important; height: auto !important; padding: 8px 16px !important; 
    border-radius: 8px !important; background: #1A1D24 !important; color: #F2F4F7 !important; 
    font-size: 14px !important; font-weight: 500 !important; border: 1px solid rgba(255,255,255,0.05) !important; 
}
.stButton button * { white-space: nowrap !important; }
.stButton button:hover { background: #282C38 !important; color: #F2F4F7 !important; }

/* Chevron Button (Only inside columns of the list) */
div[data-testid="column"] .stButton button { 
    background: transparent !important; border: none !important; color: #8A8F9E !important; 
    box-shadow: none !important; width: 40px !important; height: 40px !important; padding: 0 !important;
    border-radius: 50% !important; display: flex; align-items: center; justify-content: center; font-size: 24px !important;
}
div[data-testid="column"] .stButton button:hover { background: rgba(255,255,255,0.05) !important; color: #F2F4F7 !important; }

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
</style>
""", unsafe_allow_html=True)
