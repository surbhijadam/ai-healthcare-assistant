import streamlit as st
import os
import sys
import datetime

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_client import api_client
from components.auth_guard import require_auth

# Configure page settings
st.set_page_config(
    page_title="Medications | MediCare AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Canva-aligned CSS custom stylesheet
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Enforce authentication: only authenticated users can view medication schedules
user = require_auth(page_title="Medication Schedule")
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
    '<a href="/Dashboard" target="_self" class="canva-nav-link">Dashboard</a>'
    '<a href="/Login_Register" target="_self" class="canva-nav-link">Login / Register</a>'
        '<a href="/About" target="_self" class="canva-nav-link">About</a>'
    '<a href="/Contact" target="_self" class="canva-nav-link">Contact</a>'
    '</div>'
    f'{auth_nav_right}'
    '</div>'
    '</div>'
)
st.markdown(top_navbar_html, unsafe_allow_html=True)

# Initialize Session Medications
if "medications_list" not in st.session_state:
    st.session_state["medications_list"] = []

# Fetch live medications from backend if available
live_meds_res = api_client.get_medications()
if live_meds_res.get("success") and live_meds_res.get("data"):
    db_items = live_meds_res["data"]
    st.session_state["medications_list"] = [
        {
            "id": m.get("id"),
            "name": m.get("medication_name", "Medication"),
            "time": "08:00",
            "frequency": m.get("frequency", "Once daily"),
            "date_range": f"{m.get('start_date', '')} onwards",
            "reminder": True,
            "state": m.get("today_status", "Upcoming").lower()
        }
        for m in db_items
    ]

# ==============================================================================
# MAIN LAYOUT: TWO COLUMNS (Sidebar Left | Medication Manager Right)
# ==============================================================================
col_side, col_main = st.columns([1, 4.3], gap="large")

# ------------------------------------------------------------------------------
# LEFT COLUMN: YOUR WORKSPACE SIDEBAR (Medications Active)
# ------------------------------------------------------------------------------
with col_side:
    sidebar_html = (
        '<div class="workspace-sidebar">'
        '<div class="workspace-eyebrow">YOUR WORKSPACE</div>'
        '<a href="/Dashboard" target="_self" class="workspace-item"><span>Dashboard</span></a>'
        '<div class="workspace-divider"></div>'
        '<a href="/AI_Chatbot" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
        '<span>AI assistant</span>'
        '</a>'
        '<a href="/Medical_Reports" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
        '<span>Reports</span>'
        '</a>'
        '<a href="/Medications" target="_self" class="workspace-item active" style="background-color: #dff2f1 !important; color: #076c70 !important;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#076c70" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4.5" y1="19.5" x2="19.5" y2="4.5"></line><path d="M10.5 4.5l9 9a4.95 4.95 0 1 1-7 7l-9-9a4.95 4.95 0 1 1 7-7z"></path></svg>'
        '<span style="color: #076c70 !important; font-weight: 800;">Medications</span>'
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
# RIGHT COLUMN: MEDICATION MANAGER
# ------------------------------------------------------------------------------
with col_main:
    # Header Row: Title & Subtitle on left | + Add medication button on right
    col_h, col_btn = st.columns([3.8, 1.4])
    with col_h:
        header_html = (
            '<div style="margin-bottom: 1.8rem;">'
            '<span style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">YOUR ROUTINE</span>'
            '<h1 style="font-size: 2.15rem; font-weight: 800; color: #193648; margin: 0.25rem 0 0.4rem 0; letter-spacing: -0.02em;">Medication manager</h1>'
            '<p style="color: #637d8c; font-size: 1rem; margin: 0;">Prescription schedule tracking and daily adherence reminders.</p>'
            '</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)

    with col_btn:
        st.markdown("<div style='padding-top: 10px;' class='btn-add-med'>", unsafe_allow_html=True)
        if "show_med_form" not in st.session_state:
            st.session_state["show_med_form"] = False
        if st.button("＋ Add medication", key="btn_add_med_toggle", use_container_width=True):
            st.session_state["show_med_form"] = not st.session_state["show_med_form"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Clinical Guidance Warning Notice (FR-06.3)
    st.markdown(
        '<div style="background: #fff8eb; border-left: 4px solid #f59e0b; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px;">'
        '<strong style="color: #b45309; font-size: 0.88rem;">⚠️ Important Clinical Guidance Notice:</strong> '
        '<span style="color: #78350f; font-size: 0.85rem;">Never stop, pause, or adjust the dosage of any prescribed pharmaceutical medication without explicit consultation with your prescribing doctor or qualified healthcare professional.</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # Optional Add Medication Form Modal / Expander
    if st.session_state.get("show_med_form", False):
        with st.form("add_med_form", clear_on_submit=True):
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin: 0 0 16px 0;">Add a prescription medication</h3>', unsafe_allow_html=True)
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                med_name = st.text_input("Medication name", placeholder="e.g. Metformin / Atorvastatin")
                med_dosage = st.text_input("Dosage", placeholder="e.g. 500 mg / 10 mg")
                med_time = st.time_input("Scheduled time", datetime.time(8, 0))
            with f_col2:
                med_freq = st.selectbox("Frequency", ["Once daily", "Twice daily", "Three times daily", "As needed"])
                med_start = st.date_input("Start date", datetime.date.today())
                reminder_on = st.checkbox("Enable reminder indicator", value=True)

            sub_col1, sub_col2 = st.columns([1, 1])
            with sub_col1:
                if st.form_submit_button("Save medication", type="primary", use_container_width=True) and med_name:
                    # Save via API
                    api_client.create_medication(
                        medication_name=med_name,
                        dosage=med_dosage or "1 tablet",
                        frequency=med_freq,
                        start_date=str(med_start),
                        category="Prescription"
                    )
                    st.session_state["medications_list"].append({
                        "id": len(st.session_state["medications_list"]) + 1,
                        "name": med_name,
                        "time": med_time.strftime("%H:%M"),
                        "frequency": med_freq,
                        "date_range": f"{med_start} onwards",
                        "reminder": reminder_on,
                        "state": "upcoming"
                    })
                    st.session_state["show_med_form"] = False
                    st.success(f"Medication '{med_name}' added successfully!")
                    st.rerun()
            with sub_col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["show_med_form"] = False
                    st.rerun()

    # --------------------------------------------------------------------------
    # ACTIVE MEDICATION CARDS
    # --------------------------------------------------------------------------
    meds = st.session_state.get("medications_list", [])

    CYCLE_NEXT = {
        "upcoming": "taken",
        "taken": "skipped",
        "skipped": "upcoming"
    }
    BUTTON_TEXT = {
        "upcoming": "Upcoming · mark taken",
        "taken": "Taken · mark skipped",
        "skipped": "Skipped · reset"
    }

    if not meds:
        empty_meds_html = (
            '<div style="background: #FFFFFF; border: 1px dashed #c8dce4; border-radius: 20px; padding: 48px 24px; text-align: center; margin-bottom: 2rem;">'
            '<div style="width: 52px; height: 52px; border-radius: 16px; background: #eaf6f4; color: #087c76; display: inline-flex; align-items: center; justify-content: center; font-size: 1.6rem; margin-bottom: 1rem;">'
            '💊'
            '</div>'
            '<h3 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 6px 0;">No medications recorded</h3>'
            '<p style="color: #637d8c; font-size: 0.95rem; margin: 0 0 1.2rem 0; max-width: 420px; margin-left: auto; margin-right: auto;">'
            'Keep track of your daily prescribed medications and dosages in one calm, organized space. Click "＋ Add medication" above to record a prescription.'
            '</p>'
            '</div>'
        )
        st.markdown(empty_meds_html, unsafe_allow_html=True)
    else:
        # Render medications in 2-column grid
        for i in range(0, len(meds), 2):
            cols = st.columns(2, gap="medium")
            for j in range(2):
                if i + j < len(meds):
                    med_idx = i + j
                    med_item = meds[med_idx]
                    rem_str = "On" if med_item.get("reminder", True) else "Off"
                    cur_state = med_item.get("state", "upcoming")
                    b_label = BUTTON_TEXT.get(cur_state, "Upcoming · mark taken")

                    with cols[j]:
                        with st.container(border=True):
                            c_html = (
                                '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">'
                                '<div style="width: 44px; height: 44px; border-radius: 12px; background: #eaf6f4; display: flex; align-items: center; justify-content: center; color: #087c76;">'
                                '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#087c76" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                                '<line x1="4.5" y1="19.5" x2="19.5" y2="4.5"></line>'
                                '<path d="M10.5 4.5l9 9a4.95 4.95 0 1 1-7 7l-9-9a4.95 4.95 0 1 1 7-7z"></path>'
                                '</svg>'
                                '</div>'
                                f'<span style="background: #eaf6f4; color: #087c76; padding: 4px 14px; border-radius: 16px; font-size: 0.8rem; font-weight: 700;">{med_item.get("frequency", "Daily")}</span>'
                                '</div>'
                                f'<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 6px 0;">{med_item["name"]}</h2>'
                                f'<p style="color: #637d8c; font-size: 0.9rem; margin: 0 0 6px 0;">{med_item.get("time", "08:00")} · {med_item.get("frequency", "Daily")} · {med_item.get("date_range", "")}</p>'
                                f'<p style="color: #637d8c; font-size: 0.88rem; margin: 0 0 20px 0;">Reminder indicator: {rem_str}</p>'
                            )
                            st.markdown(c_html, unsafe_allow_html=True)
                            st.markdown('<div class="med-card-btn">', unsafe_allow_html=True)
                            if st.button(b_label, key=f"med_toggle_{med_idx}", use_container_width=True):
                                n_state = CYCLE_NEXT.get(cur_state, "upcoming")
                                med_item["state"] = n_state
                                if med_item.get("id"):
                                    api_client.toggle_dose_status(medication_id=med_item["id"], status=n_state.capitalize())
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # RECENT ADHERENCE ACTIVITY
    # --------------------------------------------------------------------------
    logged_doses = [m for m in meds if m.get("state") in ("taken", "skipped")]
    if logged_doses:
        dose_items_html = "".join([
            (
                '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">'
                f'<span style="color: #193648; font-weight: 600; font-size: 0.94rem;">{d["name"]} · {d.get("time", "Scheduled")}</span>'
                f'<span style="background: {"#eaf6f4" if d.get("state") == "taken" else "#fff3d8"}; color: {"#087c76" if d.get("state") == "taken" else "#946207"}; padding: 4px 14px; border-radius: 16px; font-size: 0.8rem; font-weight: 700;">{d.get("state", "").capitalize()}</span>'
                '</div>'
            )
            for d in logged_doses
        ])
        history_card_html = (
            '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
            '<h2 style="font-size: 1.2rem; font-weight: 800; color: #193648; margin: 0 0 18px 0;">Today’s adherence log</h2>'
            f'{dose_items_html}'
            '</div>'
        )
        st.markdown(history_card_html, unsafe_allow_html=True)

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
