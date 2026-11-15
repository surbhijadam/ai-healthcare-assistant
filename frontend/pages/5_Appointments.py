import streamlit as st
import os
import sys
import datetime
import calendar

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_client import api_client
from components.auth_guard import require_auth

# Configure page settings
st.set_page_config(
    page_title="Appointments | MediCare AI",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Canva-aligned CSS custom stylesheet
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Enforce authentication: only authenticated users can view clinical appointments
user = require_auth(page_title="Appointments")
first_name = user.get("full_name", "Patient").split()[0]
initials = "".join([p[0] for p in user.get("full_name", "P").split()[:2]]).upper() or "P"
is_admin = user.get("role") == "ROLE_ADMIN"

auth_nav_right = (
    f'<div style="display: flex; align-items: center; gap: 10px;">'
    f'<span style="color: #155c73; font-weight: 700; font-size: 0.88rem;">{first_name}</span>'
    f'<div style="width: 32px; height: 32px; border-radius: 50%; background: #d5eee9; color: #08675f; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem;">{initials}</div>'
    f'<a href="/Profile" target="_self" class="canva-nav-link" style="color: #547382; font-size: 0.86rem;">Profile</a>'
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
    '<a href="/About" target="_self" class="canva-nav-link">About</a>'
    '<a href="/Contact" target="_self" class="canva-nav-link">Contact</a>'
    '</div>'
    f'{auth_nav_right}'
    '</div>'
    '</div>'
)
st.markdown(top_navbar_html, unsafe_allow_html=True)

# Initialize Session Appointments
if "appointments_list" not in st.session_state:
    st.session_state["appointments_list"] = []

# ==============================================================================
# MAIN LAYOUT: TWO COLUMNS (Sidebar Left | Appointment Manager Right)
# ==============================================================================
col_side, col_main = st.columns([1, 4.3], gap="large")

# ------------------------------------------------------------------------------
# LEFT COLUMN: YOUR WORKSPACE SIDEBAR (Appointments Active)
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
        '<a href="/Medications" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4.5" y1="19.5" x2="19.5" y2="4.5"></line><path d="M10.5 4.5l9 9a4.95 4.95 0 1 1-7 7l-9-9a4.95 4.95 0 1 1 7-7z"></path></svg>'
        '<span>Medications</span>'
        '</a>'
        '<a href="/Appointments" target="_self" class="workspace-item active" style="background-color: #dff2f1 !important; color: #076c70 !important;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#076c70" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>'
        '<span style="color: #076c70 !important; font-weight: 800;">Appointments</span>'
        '</a>'
        '<a href="/Profile" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
        '<span>Profile</span>'
        '</a>'
        '<a href="/Admin_Panel" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
        '<span>Admin panel</span>'
        '</a>'
        '</div>'
    )
    st.markdown(sidebar_html, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# RIGHT COLUMN: APPOINTMENT MANAGER
# ------------------------------------------------------------------------------
with col_main:
    # Header Row: Title & Subtitle on left | + Add appointment button on right
    col_h, col_btn = st.columns([3.8, 1.4])
    with col_h:
        header_html = (
            '<div style="margin-bottom: 1.8rem;">'
            '<span style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">PLAN AHEAD</span>'
            '<h1 style="font-size: 2.15rem; font-weight: 800; color: #193648; margin: 0.25rem 0 0.4rem 0; letter-spacing: -0.02em;">Appointment manager</h1>'
            '<p style="color: #637d8c; font-size: 1rem; margin: 0;">Organize and track your scheduled healthcare visits.</p>'
            '</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)

    with col_btn:
        st.markdown("<div style='padding-top: 10px;' class='btn-add-apt'>", unsafe_allow_html=True)
        if "show_apt_form" not in st.session_state:
            st.session_state["show_apt_form"] = False
        if st.button("＋ Add appointment", key="btn_add_apt_toggle", use_container_width=True):
            st.session_state["show_apt_form"] = not st.session_state["show_apt_form"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Synchronize live appointments from backend
    if "appointments_list" not in st.session_state:
        st.session_state["appointments_list"] = []

    live_appts_res = api_client.get_appointments()
    if live_appts_res.get("success") and live_appts_res.get("data"):
        db_appts = live_appts_res["data"]
        st.session_state["appointments_list"] = [
            {
                "id": a.get("id"),
                "doctor": a.get("doctor_name", "Doctor"),
                "date": str(a.get("appointment_datetime", ""))[:10],
                "time": str(a.get("appointment_datetime", ""))[11:16],
                "type": f"{a.get('specialty', 'Consultation')} · {a.get('clinic_name', 'Clinic')}" if a.get('clinic_name') else a.get('specialty', 'Consultation'),
                "status": a.get("status", "upcoming").capitalize()
            }
            for a in db_appts
        ]

    # Optional Add Appointment Form Modal / Expander
    if st.session_state.get("show_apt_form", False):
        with st.form("add_apt_form", clear_on_submit=True):
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin: 0 0 16px 0;">Schedule a doctor appointment</h3>', unsafe_allow_html=True)
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                doc_input = st.text_input("Doctor name", placeholder="e.g. Dr. Priya Patel")
                spec_input = st.text_input("Specialty", placeholder="e.g. Cardiology / General Medicine")
                clinic_input = st.text_input("Clinic / Hospital", placeholder="e.g. City Healthcare Center")
            with f_col2:
                date_input = st.date_input("Date", datetime.date.today() + datetime.timedelta(days=3))
                time_input = st.time_input("Time", datetime.time(10, 30))
                notes_input = st.text_input("Discussion notes / Reason", placeholder="e.g. Routine blood panel review")

            sub_col1, sub_col2 = st.columns([1, 1])
            with sub_col1:
                if st.form_submit_button("Save appointment", type="primary", use_container_width=True) and doc_input:
                    dt_combined = datetime.datetime.combine(date_input, time_input)
                    api_client.create_appointment(
                        doctor_name=doc_input,
                        appointment_datetime=dt_combined.isoformat(),
                        specialty=spec_input or "General Consultation",
                        clinic_name=clinic_input or "Clinic",
                        notes=notes_input or "Scheduled visit"
                    )
                    st.session_state["appointments_list"].append({
                        "id": len(st.session_state["appointments_list"]) + 1,
                        "doctor": doc_input,
                        "date": str(date_input),
                        "time": time_input.strftime("%I:%M %p"),
                        "type": f"{spec_input or 'Consultation'} · {clinic_input or 'Clinic'}",
                        "status": "Upcoming"
                    })
                    st.session_state["show_apt_form"] = False
                    st.success(f"Appointment with {doc_input} scheduled!")
                    st.rerun()
            with sub_col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["show_apt_form"] = False
                    st.rerun()

    # --------------------------------------------------------------------------
    # TWO-COLUMN CONTENT: CALENDAR (LEFT) | APPOINTMENTS LIST (RIGHT)
    # --------------------------------------------------------------------------
    col_cal, col_list = st.columns([1, 1], gap="large")

    # --------------------------------------------------------------------------
    # LEFT COLUMN: CANVA CALENDAR WIDGET
    # --------------------------------------------------------------------------
    with col_cal:
        if "cal_year" not in st.session_state:
            st.session_state["cal_year"] = 2026
        if "cal_month" not in st.session_state:
            st.session_state["cal_month"] = 11

        year = st.session_state["cal_year"]
        month = st.session_state["cal_month"]
        month_name = calendar.month_name[month]

        # Calendar Container Card
        with st.container(border=True):
            # Calendar Month Navigation Header
            nav_c1, nav_c2, nav_c3 = st.columns([0.15, 0.7, 0.15])
            with nav_c1:
                st.markdown('<div class="cal-nav-btn">', unsafe_allow_html=True)
                if st.button("←", key="cal_prev_btn", use_container_width=True):
                    if st.session_state["cal_month"] == 1:
                        st.session_state["cal_month"] = 12
                        st.session_state["cal_year"] -= 1
                    else:
                        st.session_state["cal_month"] -= 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with nav_c2:
                st.markdown(
                    f'<div style="text-align: center; font-size: 1.15rem; font-weight: 800; color: #193648; padding-top: 6px;">{month_name} {year}</div>',
                    unsafe_allow_html=True
                )

            with nav_c3:
                st.markdown('<div class="cal-nav-btn">', unsafe_allow_html=True)
                if st.button("→", key="cal_next_btn", use_container_width=True):
                    if st.session_state["cal_month"] == 12:
                        st.session_state["cal_month"] = 1
                        st.session_state["cal_year"] += 1
                    else:
                        st.session_state["cal_month"] += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Generate Month Grid
            cal_obj = calendar.Calendar(firstweekday=6)  # Sunday first
            month_days = cal_obj.monthdayscalendar(year, month)

            # Marked Dates from live appointments
            marked_days = []
            for apt in st.session_state.get("appointments_list", []):
                try:
                    apt_dt = datetime.datetime.strptime(apt["date"], "%Y-%m-%d")
                    if apt_dt.year == year and apt_dt.month == month:
                        marked_days.append(apt_dt.day)
                except Exception:
                    pass

            # Build Calendar HTML
            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            headers_cells = "".join([f'<div style="color: #637d8c; font-size: 0.84rem; font-weight: 600; text-align: center; padding: 10px 0;">{d}</div>' for d in day_names])

            date_cells = ""
            for week in month_days:
                for day in week:
                    if day == 0:
                        date_cells += '<div style="height: 38px;"></div>'
                    else:
                        if day in marked_days:
                            date_cells += f'<div class="calendar-cell marked">{day}</div>'
                        else:
                            date_cells += f'<div class="calendar-cell">{day}</div>'

            calendar_grid_html = (
                '<div style="margin-top: 14px;">'
                f'<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 6px;">{headers_cells}</div>'
                f'<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px;">{date_cells}</div>'
                '<p style="color: #718a97; font-size: 0.84rem; text-align: center; margin: 28px 0 6px 0;">Highlighted dates show your scheduled consultations.</p>'
                '</div>'
            )
            st.markdown(calendar_grid_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # RIGHT COLUMN: UPCOMING APPOINTMENTS LIST
    # --------------------------------------------------------------------------
    with col_list:
        st.markdown('<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 16px 0;">Upcoming appointments</h2>', unsafe_allow_html=True)

        appts = st.session_state.get("appointments_list", [])
        if not appts:
            empty_html = (
                '<div style="background: #FFFFFF; border: 1.5px dashed #b9d8d5; border-radius: 20px; padding: 42px 28px; text-align: center; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
                '<div style="font-size: 2.2rem; margin-bottom: 12px;">📅</div>'
                '<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin: 0 0 8px 0;">No appointments scheduled yet</h3>'
                '<p style="color: #637d8c; font-size: 0.92rem; margin: 0; line-height: 1.5;">Click the <strong>＋ Add appointment</strong> button above to log an upcoming doctor or clinic visit.</p>'
                '</div>'
            )
            st.markdown(empty_html, unsafe_allow_html=True)
        else:
            for apt in appts:
                status_color = "#087c76" if apt.get("status", "").lower() in ("confirmed", "scheduled") else "#1a6c8e"
                status_bg = "#eaf6f4" if apt.get("status", "").lower() in ("confirmed", "scheduled") else "#e8f2f8"
                card_html = (
                    '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 22px 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); margin-bottom: 16px;">'
                    f'<span style="background: {status_bg}; color: {status_color}; padding: 4px 14px; border-radius: 16px; font-size: 0.8rem; font-weight: 700; display: inline-block; margin-bottom: 10px;">{apt.get("status", "Scheduled")}</span>'
                    f'<h3 style="font-size: 1.2rem; font-weight: 800; color: #193648; margin: 0 0 6px 0;">{apt.get("doctor", "Doctor")}</h3>'
                    f'<p style="color: #637d8c; font-size: 0.9rem; margin: 0 0 4px 0;">{apt.get("date", "")} · {apt.get("time", "")}</p>'
                    f'<p style="color: #637d8c; font-size: 0.88rem; margin: 0;">{apt.get("type", "Consultation")}</p>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

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
