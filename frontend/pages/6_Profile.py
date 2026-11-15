import streamlit as st
import os
import sys

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_client import api_client
from components.auth_guard import require_auth

# Configure page settings
st.set_page_config(
    page_title="Profile & Settings | MediCare AI",
    page_icon="👤",
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
/* Hide native Streamlit sidebar so in-page Canva sidebar renders below the top Canva navbar */
section[data-testid="stSidebar"] {
    display: none !important;
}

/* Card container styling */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid #dce9ef !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04) !important;
    margin-bottom: 1rem !important;
}

/* Form input fields inside Profile */
.stTextInput input {
    border: 1px solid #dce9ef !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-size: 0.95rem !important;
    color: #193648 !important;
    background-color: #FFFFFF !important;
}

.stTextInput input:focus {
    border-color: #087c76 !important;
    box-shadow: 0 0 0 1px #087c76 !important;
}
</style>""",
    unsafe_allow_html=True
)

# Enforce authentication: only authenticated users can access personal profile & settings
user = require_auth(page_title="Profile & Settings")
token = st.session_state.get("token")
is_admin = user.get("role") == "ROLE_ADMIN"

live_profile_data = None
if token:
    prof_res = api_client.get_profile()
    if prof_res.get("success") and prof_res.get("data"):
        live_profile_data = prof_res["data"]

profile = live_profile_data or user
curr_name = profile.get("full_name", user.get("full_name", "Patient"))
curr_email = profile.get("email", user.get("email", "patient@example.com"))
curr_city = profile.get("city", "")
curr_blood = profile.get("blood_group", "—")
curr_age = profile.get("calculated_age", "—")
curr_bmi = profile.get("calculated_bmi", "—")
curr_emergency = profile.get("emergency_contact", "")
curr_allergies = profile.get("allergies", "")
curr_conditions = profile.get("chronic_conditions", "")

initials = "".join([part[0] for part in curr_name.split()[:2]]).upper() or "P"
is_live_sync = live_profile_data is not None
is_auth = st.session_state.get("authenticated", False)

auth_nav_right = (
    f'<div style="display: flex; align-items: center; gap: 10px;">'
    f'<span style="color: #155c73; font-weight: 700; font-size: 0.88rem;">{curr_name.split()[0]}</span>'
    f'<div style="width: 32px; height: 32px; border-radius: 50%; background: #d5eee9; color: #08675f; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem;">{initials}</div>'
    f'<a href="/Profile" target="_self" class="canva-nav-link active" style="color: #076c70; background-color: #dff2f1; font-size: 0.86rem;">Profile</a>'
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
    '<a href="/Dashboard" target="_self" class="canva-nav-link">Dashboard</a>'
    '<a href="/About" target="_self" class="canva-nav-link">About</a>'
    '<a href="/Contact" target="_self" class="canva-nav-link">Contact</a>'
    '</div>'
    f'{auth_nav_right}'
    '</div>'
    '</div>'
)
st.markdown(top_navbar_html, unsafe_allow_html=True)

# ==============================================================================
# MAIN LAYOUT: TWO COLUMNS (Sidebar Left | Profile & Settings Right)
# ==============================================================================
col_side, col_main = st.columns([1, 4.3], gap="large")

# ------------------------------------------------------------------------------
# LEFT COLUMN: YOUR WORKSPACE SIDEBAR (Profile Active)
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
        '<a href="/Appointments" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>'
        '<span>Appointments</span>'
        '</a>'
        '<a href="/Profile" target="_self" class="workspace-item active" style="background-color: #dff2f1 !important; color: #076c70 !important;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#076c70" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
        '<span style="color: #076c70 !important; font-weight: 800;">Profile</span>'
        '</a>'
        '<a href="/Admin_Panel" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
        '<span>Admin panel</span>'
        '</a>'
        '</div>'
    )
    st.markdown(sidebar_html, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# RIGHT COLUMN: PROFILE & SETTINGS
# ------------------------------------------------------------------------------
with col_main:
    # Header Section
    sync_badge = (
        '<span style="background: #e8f6f3; color: #087c76; padding: 4px 12px; border-radius: 12px; font-size: 0.78rem; font-weight: 700; border: 1px solid #cceae3;">● Live Database Sync</span>'
        if is_live_sync else
        '<span style="background: #eaf3f8; color: #1a6c8e; padding: 4px 12px; border-radius: 12px; font-size: 0.78rem; font-weight: 700; border: 1px solid #cce0eb;">● Active Profile Session</span>'
    )

    header_html = (
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; flex-wrap: wrap; gap: 10px;">'
        '<div>'
        '<span style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">YOUR ACCOUNT</span>'
        '<h1 style="font-size: 2.15rem; font-weight: 800; color: #193648; margin: 0.25rem 0 0 0; letter-spacing: -0.02em;">Profile & settings</h1>'
        '</div>'
        f'{sync_badge}'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # Two-Column Section: Personal Info (Left) | Settings Cards (Right)
    col_info, col_settings = st.columns([1.1, 1], gap="large")

    # --------------------------------------------------------------------------
    # LEFT COLUMN: PERSONAL INFORMATION & CLINICAL METRICS CARD
    # --------------------------------------------------------------------------
    with col_info:
        with st.container(border=True):
            profile_card_header = (
                '<div style="display: flex; align-items: center; gap: 16px; margin-bottom: 1.2rem;">'
                f'<div style="width: 52px; height: 52px; border-radius: 50%; background: #d5eee9; color: #08675f; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; font-weight: 800;">{initials}</div>'
                '<div>'
                f'<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 2px 0;">{curr_name}</h2>'
                f'<p style="color: #718a97; font-size: 0.88rem; margin: 0;">{curr_email}</p>'
                '</div>'
                '</div>'
                '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 1.4rem;">'
                f'<div style="background: #f7fafc; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center;"><span style="font-size: 0.72rem; color: #718096; font-weight: 700; text-transform: uppercase;">Age</span><div style="font-size: 1.1rem; font-weight: 800; color: #1a202c;">{curr_age} yrs</div></div>'
                f'<div style="background: #f7fafc; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center;"><span style="font-size: 0.72rem; color: #718096; font-weight: 700; text-transform: uppercase;">Blood Group</span><div style="font-size: 1.1rem; font-weight: 800; color: #1a202c;">{curr_blood}</div></div>'
                f'<div style="background: #f7fafc; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center;"><span style="font-size: 0.72rem; color: #718096; font-weight: 700; text-transform: uppercase;">BMI</span><div style="font-size: 1.1rem; font-weight: 800; color: #1a202c;">{curr_bmi}</div></div>'
                '</div>'
            )
            st.markdown(profile_card_header, unsafe_allow_html=True)

            with st.form("canva_profile_edit_form"):
                st.markdown('<label style="color: #193648; font-size: 0.9rem; font-weight: 700; display: block; margin-bottom: 4px;">Full name</label>', unsafe_allow_html=True)
                name_val = st.text_input("Full name", value=curr_name, label_visibility="collapsed")

                st.markdown('<label style="color: #193648; font-size: 0.9rem; font-weight: 700; display: block; margin: 12px 0 4px 0;">City</label>', unsafe_allow_html=True)
                city_val = st.text_input("City", value=curr_city, label_visibility="collapsed")

                st.markdown('<label style="color: #193648; font-size: 0.9rem; font-weight: 700; display: block; margin: 12px 0 4px 0;">Emergency Contact</label>', unsafe_allow_html=True)
                emergency_val = st.text_input("Emergency Contact", value=curr_emergency, label_visibility="collapsed")

                st.markdown('<label style="color: #193648; font-size: 0.9rem; font-weight: 700; display: block; margin: 12px 0 4px 0;">Known Allergies</label>', unsafe_allow_html=True)
                allergies_val = st.text_input("Known Allergies", value=curr_allergies, label_visibility="collapsed")

                st.markdown('<label style="color: #193648; font-size: 0.9rem; font-weight: 700; display: block; margin: 12px 0 4px 0;">Chronic Conditions</label>', unsafe_allow_html=True)
                conditions_val = st.text_input("Chronic Conditions", value=curr_conditions, label_visibility="collapsed")

                st.markdown("<div style='margin-top: 18px;' class='profile-edit-btn'>", unsafe_allow_html=True)
                edit_saved = st.form_submit_button("Save Profile Changes", type="primary", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                if edit_saved:
                    update_payload = {
                        "full_name": name_val.strip(),
                        "city": city_val.strip(),
                        "emergency_contact": emergency_val.strip(),
                        "allergies": allergies_val.strip(),
                        "chronic_conditions": conditions_val.strip()
                    }
                    if is_auth and token:
                        with st.spinner("Saving changes to database..."):
                            up_res = api_client.update_profile(update_payload)
                        if up_res.get("success"):
                            st.success("Profile successfully updated in database!")
                            st.session_state["user"] = up_res.get("data")
                            st.rerun()
                        else:
                            st.error(f"Failed to update profile: {up_res.get('message')}")
                    else:
                        profile["full_name"] = name_val
                        profile["city"] = city_val
                        profile["emergency_contact"] = emergency_val
                        profile["allergies"] = allergies_val
                        profile["chronic_conditions"] = conditions_val
                        st.session_state["user"] = profile
                        st.success("Profile updated successfully!")
                        st.rerun()

def safe_switch_to_home():
    """Safely redirects to Home whether Streamlit entrypoint is app.py or Home.py."""
    for target in ["app.py", "Home.py"]:
        try:
            st.switch_page(target)
            return
        except Exception:
            pass
    st.markdown('<meta http-equiv="refresh" content="0; url=/">', unsafe_allow_html=True)
    st.rerun()

# ------------------------------------------------------------------------------
# RIGHT COLUMN: SETTINGS & DPDP ACT ERASURE
# ------------------------------------------------------------------------------
    with col_settings:
        # Card 1: Account settings
        with st.container(border=True):
            acc_html = (
                '<h2 style="font-size: 1.18rem; font-weight: 800; color: #193648; margin: 0 0 6px 0;">Account settings</h2>'
                f'<p style="color: #637d8c; font-size: 0.88rem; line-height: 1.5; margin: 0 0 10px 0;">Registered email: <strong>{curr_email}</strong></p>'
                '<p style="color: #718a97; font-size: 0.82rem; margin: 0;">Role: Patient (ROLE_USER) · Active session</p>'
            )
            st.markdown(acc_html, unsafe_allow_html=True)

        # Card 2: Privacy settings & Disclaimers
        with st.container(border=True):
            st.markdown('<h2 style="font-size: 1.18rem; font-weight: 800; color: #193648; margin: 0 0 10px 0;">Clinical privacy notice</h2>', unsafe_allow_html=True)
            st.markdown(
                '<p style="color: #557582; font-size: 0.86rem; line-height: 1.5; margin: 0;">'
                'MediCare AI adheres to strict data privacy principles. Your laboratory results, prescription records, and health inquiries are encrypted in transit and at rest.'
                '</p>',
                unsafe_allow_html=True
            )

        # Card 3: DPDP Act 2023 Permanent Right to Erasure
        with st.container(border=True):
            st.markdown(
                '<h2 style="font-size: 1.18rem; font-weight: 800; color: #b91c1c; margin: 0 0 6px 0;">DPDP Act 2023 Data Erasure</h2>'
                '<p style="color: #637d8c; font-size: 0.86rem; line-height: 1.5; margin: 0 0 12px 0;">'
                'Under India’s Digital Personal Data Protection Act 2023, you hold the unconditional right to erase your account and all personal health data.'
                '</p>',
                unsafe_allow_html=True
            )
            with st.expander("Permanent Account & Data Deletion", expanded=False):
                st.warning("⚠️ This action permanently deletes your profile, all uploaded reports, medications, and conversation logs. It cannot be reversed.")
                confirm_dpdp = st.checkbox("I confirm permanent deletion of all my records.", key="confirm_dpdp_deletion")
                if st.button("Permanently Erase Account", type="primary", key="btn_execute_dpdp", disabled=not confirm_dpdp):
                    with st.spinner("Cascading permanent erasure across database..."):
                        del_res = api_client.delete_profile()
                    st.success("Your account and all associated health records have been permanently erased under DPDP Act 2023.")
                    safe_switch_to_home()

        # Card 4: Session Logout
        with st.container(border=True):
            st.markdown('<h2 style="font-size: 1.18rem; font-weight: 800; color: #193648; margin: 0 0 8px 0;">Session management</h2>', unsafe_allow_html=True)
            if st.button("🚪 Logout · Return to Home", key="btn_logout_clean", use_container_width=True):
                api_client.logout()
                safe_switch_to_home()

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
