import streamlit as st

def load_global_css():
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

/* GLOBALS PARA EXTENDER LA UI COMPLETAMENTE A LO ANCHO Y ALTO */
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap: 12px !important; }

/* Separación entre elementos horizontales generales */
[data-testid="stHorizontalBlock"] { gap: 20px !important; padding: 0 40px !important; margin-bottom: 20px !important; }
div[data-testid="column"] { padding: 0 !important; }

/* ── SIDEBAR (Fondo Oscuro Premium) ── */
[data-testid="stSidebar"] { background-color: #16181F !important; width: 260px !important; min-width: 260px !important; border-right: none !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; background-color: #16181F !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding: 0 !important; gap: 0 !important; }

.sidebar-wrap { display: flex; flex-direction: column; position: fixed; top: 0; left: 0; bottom: 0; width: 260px; background: #16181F; padding-top: 32px; box-sizing: border-box; z-index: 999999; }
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

.sidebar-footer { padding: 16px; margin-top: auto; border-top: 1px solid rgba(255,255,255,0.05); }
.logout-btn { color: #E97358 !important; }
.logout-btn i { color: #E97358 !important; }

/* ── TOPBAR (Transparente) ── */
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 32px 40px 24px; margin-bottom: 16px; }
.topbar-left { display: flex; align-items: center; gap: 24px; }
.topbar h1 { font-size: 24px; font-weight: 700; color: #F2F4F7; margin: 0; padding: 0; letter-spacing: -0.02em; }
.topbar-title-sep { width: 1px; height: 24px; background: #282C38; }
.topbar-subtitle { font-size: 14px; color: #8A8F9E; font-weight: 500; }

.topbar-right { display: flex; align-items: center; gap: 16px; }
.icon-btn { position: relative; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #1A1D24; color: #F2F4F7; font-size: 20px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); transition: 0.2s; }
.icon-btn:hover { background: #282C38; }
.icon-btn.has-notification::after { content: ''; position: absolute; top: 10px; right: 12px; width: 8px; height: 8px; background: #E97358; border-radius: 50%; box-shadow: 0 0 8px rgba(233,115,88,0.8); }

.profile-pill { display: flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 600; color: #F2F4F7; background: #1A1D24; padding: 6px 20px 6px 6px; border-radius: 99px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); transition: 0.2s; }
.profile-pill:hover { background: #282C38; }
.profile-avatar { width: 36px; height: 36px; border-radius: 50%; background: #D0ED57; display: flex; align-items: center; justify-content: center; color: #16181F; font-size: 14px; font-weight: 700; }

/* ── TICKET NOTIFICATION CLASSES ── */
.ticket-new-badge { font-size: 10px; background: rgba(208,237,87,0.15); color: #D0ED57; padding: 2px 6px; border-radius: 4px; font-weight: 700; margin-left: 8px; vertical-align: middle; }
.ticket-card.is-new { border-color: rgba(208,237,87,0.4) !important; box-shadow: 0 0 16px rgba(208,237,87,0.1) !important; }

/* ── UTILS ── */
.px { padding: 0 40px; margin-bottom: 32px; }
</style>
    """, unsafe_allow_html=True)

def render_sidebar(active_page="dashboard"):
    dash_active = "active" if active_page == "dashboard" else ""
    tickets_active = "active" if active_page == "tickets" else ""
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-wrap">
            <span class="sidebar-menu-label">MENÚ PRINCIPAL</span>
            <div class="sidebar-nav">
                <a class="nav-btn {dash_active}" href="/" target="_self"><i class="mdi mdi-view-dashboard"></i> Dashboard</a>
                <a class="nav-btn {tickets_active}" href="/tickets" target="_self"><i class="mdi mdi-ticket-confirmation-outline"></i> Tickets</a>
            </div>
            <div class="sidebar-footer">
                <a class="nav-btn logout-btn" href="#"><i class="mdi mdi-logout"></i> Cerrar sesión</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_topbar(subtitle="Panel de análisis", has_notifications=False):
    bell_class = "has-notification" if has_notifications else ""
    st.markdown(f"""
    <div class="topbar">
      <div class="topbar-left">
        <h1>ConversaAI</h1>
        <div class="topbar-title-sep"></div>
        <span class="topbar-subtitle">{subtitle}</span>
      </div>
      <div class="topbar-right">
        <div class="icon-btn {bell_class}"><i class="mdi mdi-bell-outline"></i></div>
        <div class="profile-pill">
          <div class="profile-avatar">P</div> Pablo Diaz
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
