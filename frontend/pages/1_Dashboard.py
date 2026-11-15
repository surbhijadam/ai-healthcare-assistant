import streamlit as st
import os
import sys
import importlib

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_client import api_client
from components.auth_guard import require_auth
import components.cards
importlib.reload(components.cards)
from components.cards import render_stat_card, render_adherence_widget, render_wellness_chart_svg

# Configure page settings
st.set_page_config(
    page_title="Dashboard | MediCare AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Canva-aligned CSS custom stylesheet
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page-specific layout & sidebar overrides
st.markdown(
    """<style>
section[data-testid="stSidebar"] {
    display: none !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid #dce9ef !important;
    border-radius: 22px !important;
    padding: 24px !important;
    box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04) !important;
}
</style>""",
    unsafe_allow_html=True
)

# Enforce authentication: only authenticated users can access the personal dashboard
user = require_auth(page_title="Dashboard")
first_name = user.get("full_name", "Patient").split()[0]
initials = "".join([p[0] for p in user.get("full_name", "P").split()[:2]]).upper() or "P"
is_admin = user.get("role") == "ROLE_ADMIN"

auth_nav_right = (
    f'<div style="display: flex; align-items: center; gap: 10px;">'
    f'<span style="color: #155c73; font-weight: 700; font-size: 0.88rem;">{first_name}</span>'
    f'<div style="width: 32px; height: 32px; border-radius: 50%; background: #d5eee9; color: #08675f; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem;">{initials}</div>'
    f'<a href="/Profile" target="_self" class="canva-nav-link" style="color: #547382; font-size: 0.86rem;">Profile</a>'
    '<a href="/Login_Register" target="_self" class="canva-nav-link" style="color: #087c76; font-size: 0.86rem; font-weight: 700;">Login / Switch</a>'
    f'</div>'
)

# ==============================================================================
# TOP NAVBAR (100% Canva Layout: Logo Left | Menu Center | Auth Right)
# ==============================================================================
top_navbar_html = (
    '<div style="background: #FFFFFF; border-bottom: 1px solid #dce9ef; padding: 12px 24px; border-radius: 16px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
    '<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">'
    '<div style="display: flex; align-items: center; gap: 10px;">'
    '<span class="iconbox" style="margin: 0; width: 38px; height: 38px; font-size: 1.15rem; background: #e8f6f3; color: #087c76;">🩺</span>'
    '<span style="color: #155c73; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;">MediCare AI</span>'
    '</div>'
    '<div style="display: flex; align-items: center; gap: 16px; font-weight: 700; font-size: 0.92rem;">'
    '<a href="/" target="_self" class="canva-nav-link">Home</a>'
    '<a href="/#features" target="_self" class="canva-nav-link">Features</a>'
    '<a href="/Dashboard" target="_self" class="canva-nav-link active" style="color: #076c70; background-color: #dff2f1;">Dashboard</a>'
    '<a href="/Login_Register" target="_self" class="canva-nav-link">Login / Register</a>'
        '<a href="/About" target="_self" class="canva-nav-link">About</a>'
    '<a href="/Contact" target="_self" class="canva-nav-link">Contact</a>'
    '</div>'
    f'{auth_nav_right}'
    '</div>'
    '</div>'
)
st.markdown(top_navbar_html, unsafe_allow_html=True)

# Gather dynamic metrics from API
metrics = api_client.get_dashboard_metrics()
is_live = metrics.get("is_live", False)
conn_badge = (
    '<span style="background: #e8f6f3; color: #087c76; padding: 4px 12px; border-radius: 12px; font-size: 0.76rem; font-weight: 700; border: 1px solid #cceae3;">● Live Connected</span>'
    if is_live else
    '<span style="background: #eaf3f8; color: #1a6c8e; padding: 4px 12px; border-radius: 12px; font-size: 0.76rem; font-weight: 700; border: 1px solid #cce0eb;">● Active Session</span>'
)

# ==============================================================================
# MAIN LAYOUT: TWO COLUMNS (Sidebar Left | Workspace Dashboard Right)
# ==============================================================================
col_side, col_main = st.columns([1, 4.3], gap="large")

# ------------------------------------------------------------------------------
# LEFT COLUMN: YOUR WORKSPACE SIDEBAR
# ------------------------------------------------------------------------------
with col_side:
    sidebar_html = (
        '<div class="workspace-sidebar">'
        '<div class="workspace-eyebrow">YOUR WORKSPACE</div>'
        '<a href="/Dashboard" target="_self" class="workspace-item active"><span>Dashboard</span></a>'
        '<div class="workspace-divider"></div>'
        '<a href="/AI_Chatbot" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
        '<span>AI assistant</span>'
        '</a>'
        '<a href="/Medical_Reports" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
        '<span>Reports</span>'
        '</a>'
        '<a href="/Medications" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4.5" y1="19.5" x2="19.5" y2="4.5"></line><path d="M10.5 4.5l9 9a4.95 4.95 0 1 1-7 7l-9-9a4.95 4.95 0 1 1 7-7z"></path></svg>'
        '<span>Medications</span>'
        '</a>'
        '<a href="/Appointments" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>'
        '<span>Appointments</span>'
        '</a>'
        '<a href="/Profile" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
        '<span>Profile</span>'
        '</a>'
        '<a href="/Admin_Panel" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
        '<span>Admin panel</span>'
        '</a>'
        '<div class="workspace-divider"></div>'
        '<a href="/Login_Register" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>'
        '<span>Login / Register</span>'
        '</a>'
        '</div>'
    )
    st.markdown(sidebar_html, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# RIGHT COLUMN: MAIN WORKSPACE DASHBOARD
# ------------------------------------------------------------------------------
with col_main:
    # Sub-header Row: Date on left | Notification Bell, Connection Badge & Avatar on right
    header_row_html = (
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.4rem; flex-wrap: wrap; gap: 10px;">'
        '<span style="color: #637d8c; font-size: 0.88rem; font-weight: 500;">Personal overview · 14 November 2026</span>'
        '<div style="display: flex; align-items: center; gap: 12px;">'
        f'{conn_badge}'
        '<div style="width: 38px; height: 38px; border-radius: 50%; background: #f0f8f6; border: 1px solid #cce9e2; display: flex; align-items: center; justify-content: center; cursor: pointer;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#087c76" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>'
        '</div>'
        f'<div style="width: 38px; height: 38px; border-radius: 50%; background: #d5eee9; color: #08675f; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.95rem;">{initials}</div>'
        '</div>'
        '</div>'
    )
    st.markdown(header_row_html, unsafe_allow_html=True)

    # Greeting Section
    greeting_html = (
        '<div style="margin-bottom: 2rem;">'
        '<span style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">YOUR HEALTH SPACE</span>'
        '<h1 style="font-size: 2.15rem; font-weight: 800; color: #193648; margin: 0.25rem 0 0.4rem 0; letter-spacing: -0.02em;">Welcome back!</h1>'
        f'<p style="color: #637d8c; font-size: 1rem; margin: 0;">Here is your personal overview, {first_name}.</p>'
        '</div>'
    )
    st.markdown(greeting_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 1: 3 CANVA STATISTICS CARDS (Dynamic Backend-Connected)
    # --------------------------------------------------------------------------
    doc_icon_svg = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#087c76" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
    pill_icon_svg = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#087c76" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4.5" y1="19.5" x2="19.5" y2="4.5"></line><path d="M10.5 4.5l9 9a4.95 4.95 0 1 1-7 7l-9-9a4.95 4.95 0 1 1 7-7z"></path></svg>'
    cal_icon_svg = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#087c76" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>'

    col1, col2, col3 = st.columns(3)
    with col1:
        render_stat_card("Total medical reports", metrics["total_reports"], doc_icon_svg)
    with col2:
        render_stat_card("Active medication records", metrics["active_medications"], pill_icon_svg)
    with col3:
        render_stat_card("Upcoming appointments", metrics["upcoming_appointments"], cal_icon_svg)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 2: WELLNESS TREND & MEDICATION ADHERENCE (Dynamic Adherence)
    # --------------------------------------------------------------------------
    c_chart, c_adh = st.columns([1.4, 1], gap="medium")

    with c_chart:
        render_wellness_chart_svg()

    with c_adh:
        render_adherence_widget(recorded=metrics["adherence_recorded"], total=metrics["adherence_total"])

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 3: RECENT ACTIVITY & QUICK ACTIONS (Dynamic Activity Items)
    # --------------------------------------------------------------------------
    col_act, col_qa = st.columns([1, 1], gap="medium")

    with col_act:
        with st.container(border=True):
            recent_acts = metrics.get("recent_activity", [])
            if not recent_acts:
                activity_content_html = (
                    '<div style="text-align: center; padding: 22px 10px; color: #718a97;">'
                    '<p style="font-size: 0.92rem; margin: 0 0 4px 0;">No recent actions logged yet.</p>'
                    '<span style="font-size: 0.82rem;">Upload a report, track a dose, or ask the AI assistant to see your history here.</span>'
                    '</div>'
                )
            else:
                activity_items_html = ""
                for act in recent_acts:
                    icon = act.get("icon", "📄")
                    title = act.get("title", "Clinical update")
                    date_str = act.get("date", "Recent")
                    activity_items_html += (
                        '<div style="display: flex; align-items: center; gap: 14px;">'
                        f'<div style="width: 36px; height: 36px; border-radius: 10px; background: #f0f2f8; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">{icon}</div>'
                        f'<div><strong style="color: #193648; font-size: 0.94rem; display: block; font-weight: 700;">{title}</strong><span style="color: #718a97; font-size: 0.82rem;">{date_str}</span></div>'
                        '</div>'
                    )
                activity_content_html = f'<div style="display: flex; flex-direction: column; gap: 18px;">{activity_items_html}</div>'

            recent_act_html = (
                '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 18px 0;">Recent activity</h2>'
                f'{activity_content_html}'
            )
            st.markdown(recent_act_html, unsafe_allow_html=True)

    with col_qa:
        with st.container(border=True):
            st.markdown('<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 22px 0;">Quick actions</h2>', unsafe_allow_html=True)
            qa1, qa2 = st.columns(2)
            with qa1:
                btn_chat = st.button("✦ Ask the assistant", key="qa_btn_chat", use_container_width=True)
                btn_meds = st.button("⏱ Track a dose", key="qa_btn_meds", use_container_width=True)
            with qa2:
                btn_reports = st.button("📄 View reports", key="qa_btn_reports", use_container_width=True)
                btn_appts = st.button("▦ See appointments", key="qa_btn_appts", use_container_width=True)

            if btn_chat:
                st.switch_page("pages/2_AI_Chatbot.py")
            if btn_meds:
                st.switch_page("pages/4_Medications.py")
            if btn_reports:
                st.switch_page("pages/3_Medical_Reports.py")
            if btn_appts:
                st.switch_page("pages/5_Appointments.py")

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 4: WELLNESS REMINDER CARD
    # --------------------------------------------------------------------------
    reminder_html = (
        '<div style="background: #eaf7f4; border: 1px solid #c7e8e1; border-radius: 20px; padding: 22px 28px;">'
        '<h2 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin: 0 0 8px 0;">A small wellness reminder</h2>'
        '<p style="color: #557582; font-size: 0.92rem; line-height: 1.6; margin: 0;">Bring a list of questions to your next healthcare appointment. Your care team is the best source for advice about your individual health.</p>'
        '</div>'
    )
    st.markdown(reminder_html, unsafe_allow_html=True)

# ==============================================================================
# CANVA DARK FOOTER (#193c4c) - FULL CONTAINER WIDTH
# ==============================================================================
st.markdown("<div style='margin-top: 3.5rem;'></div>", unsafe_allow_html=True)
footer_html = (
    '<div class="canva-footer" style="background: #193c4c; color: #FFFFFF; border-radius: 20px; padding: 2.5rem 2.2rem; margin-top: 2rem;">'
    '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 28px; align-items: flex-start;">'
    '<div>'
    '<strong style="font-size: 1.25rem; display: flex; align-items: center; gap: 8px; color: #FFFFFF;">✚ MediCare AI</strong>'
    '<p style="color: #FFFFFF !important; font-size: 0.88rem; margin-top: 10px; line-height: 1.6;">A more understandable way to explore everyday health information.</p>'
    '</div>'
    '<div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.88rem; color: #FFFFFF;">'
    '<div style="display: flex; gap: 16px; flex-wrap: wrap;">'
    '<a href="/" target="_self" style="color: #FFFFFF !important; text-decoration: none; font-weight: 600;">Home</a>'
    '<a href="/#features" target="_self" style="color: #FFFFFF !important; text-decoration: none; font-weight: 600;">Features</a>'
    '<a href="/About" target="_self" style="color: #FFFFFF !important; text-decoration: none; font-weight: 600;">About</a>'
    '<a href="/Login_Register" target="_self" style="color: #FFFFFF !important; text-decoration: none; font-weight: 600;">Login / Register</a>'
    '<a href="/Contact" target="_self" style="color: #FFFFFF !important; text-decoration: none; font-weight: 600;">Contact</a>'
    '<a href="/Dashboard" target="_self" style="color: #FFFFFF !important; text-decoration: none; font-weight: 600;">Dashboard</a>'
    '</div>'
    '</div>'
    '<div style="font-size: 0.86rem; color: #FFFFFF;">'
    '<p style="color: #FFFFFF !important; margin: 0 0 6px 0;">hello@medicareai.example</p>'
    '<p style="color: #FFFFFF !important; margin: 0 0 6px 0;">Educational information only. Not medical advice.</p>'
    '<p style="color: #FFFFFF !important; margin: 0 0 6px 0;">© 2026 MediCare AI · All rights reserved</p>'
    '</div>'
    '</div>'
    '</div>'
)
st.markdown(footer_html, unsafe_allow_html=True)
