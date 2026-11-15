import streamlit as st
import os
import sys

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_client import api_client
from components.auth_guard import require_auth

# Configure page settings
st.set_page_config(
    page_title="Medical Reports | MediCare AI",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Canva-aligned CSS custom stylesheet
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Enforce authentication: only authenticated users can view clinical reports
user = require_auth(page_title="Medical Reports")
first_name = user.get("full_name", "Patient").split()[0]
initials = "".join([p[0] for p in user.get("full_name", "P").split()[:2]]).upper() or "P"
is_admin = user.get("role") == "ROLE_ADMIN"

# Page-specific layout & sidebar overrides
st.markdown(
    """<style>
/* Hide native Streamlit sidebar so in-page Canva sidebar renders below the top Canva navbar */
section[data-testid="stSidebar"] {
    display: none !important;
}

/* White Card Containers */
.report-card {
    background: #FFFFFF !important;
    border: 1px solid #dce9ef !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04) !important;
    margin-bottom: 1.5rem !important;
}

/* Multi-step form button styling */
.step-nav-btn button {
    border-radius: 10px !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.4rem !important;
}
</style>""",
    unsafe_allow_html=True
)

# ==============================================================================
# TOP NAVBAR (100% Canva Layout: Logo Left | Menu Center | Auth Right)
# ==============================================================================
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

# ==============================================================================
# MAIN LAYOUT: TWO COLUMNS (Sidebar Left | Medical Reports & Profile Right)
# ==============================================================================
col_side, col_main = st.columns([1, 4.3], gap="large")

# ------------------------------------------------------------------------------
# LEFT COLUMN: YOUR WORKSPACE SIDEBAR (Reports Active)
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
        '<a href="/Medical_Reports" target="_self" class="workspace-item active" style="background-color: #dff2f1 !important; color: #076c70 !important;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#076c70" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
        '<span style="color: #076c70 !important; font-weight: 800;">Reports</span>'
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
# RIGHT COLUMN: MEDICAL REPORT ASSISTANT & PATIENT HEALTH PROFILE
# ------------------------------------------------------------------------------
with col_main:
    # Header Section
    header_html = (
        '<div style="margin-bottom: 1.2rem;">'
        '<span style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">DOCUMENT CLARITY & HEALTH PROFILES</span>'
        '<h1 style="font-size: 2.15rem; font-weight: 800; color: #193648; margin: 0.25rem 0 0.4rem 0; letter-spacing: -0.02em;">Medical report assistant</h1>'
        '<p style="color: #637d8c; font-size: 1rem; margin: 0;">A structured overview of extracted lab values and educational explanations side by side.</p>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 13: RECOMMENDED PATIENT HEALTH PROFILE (MULTI-STEP FORM UI)
    # ==========================================================================
    if "profile_step" not in st.session_state:
        st.session_state["profile_step"] = 1

    curr_step = max(1, min(8, st.session_state["profile_step"]))
    step_pct = int((curr_step / 8) * 100)

    step_titles = {
        1: ("Basic Information", "Enter your basic personal details for clinical context."),
        2: ("Emergency Contact Information", "Designate trusted contacts who can be reached in medical emergencies."),
        3: ("Medical History", "Record existing medical conditions, past surgeries, and hospitalizations."),
        4: ("Known Allergies", "Critical for safe clinical context and counter-indication warnings."),
        5: ("Current Medications", "Record existing prescriptions and dosage schedules."),
        6: ("Lifestyle & Health Habits", "Contextualize health observations with everyday lifestyle habits."),
        7: ("Health Measurements & Vital Signs", "Record baseline vitals with date, time, units, and clinical context."),
        8: ("Consent, Privacy & Data Authorization", "Explicit, revocable authorizations governing sensitive health data.")
    }

    step_title, step_desc = step_titles[curr_step]

    stepper_header_html = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px 24px 18px 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); margin-bottom: 1.5rem;">'
        '<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">'
        '<div>'
        '<span style="background: #eaf6f4; color: #087c76; padding: 4px 12px; border-radius: 12px; font-size: 0.76rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase;">PATIENT HEALTH PROFILE</span>'
        f'<h2 style="font-size: 1.35rem; font-weight: 800; color: #193648; margin: 8px 0 2px 0;">{step_title}</h2>'
        f'<p style="color: #637d8c; font-size: 0.88rem; margin: 0;">{step_desc}</p>'
        '</div>'
        '<div style="text-align: right;">'
        f'<span style="font-size: 0.95rem; font-weight: 800; color: #087c76;">Step {curr_step} of 8</span>'
        f'<span style="font-size: 0.82rem; color: #718a97; margin-left: 8px;">({step_pct}% completed)</span>'
        '</div>'
        '</div>'
        '<div style="width: 100%; height: 7px; background: #eef5f7; border-radius: 4px; overflow: hidden; margin-top: 10px;">'
        f'<div style="width: {step_pct}%; height: 100%; background: #087c76; border-radius: 4px; transition: width 0.3s ease;"></div>'
        '</div>'
        '</div>'
    )
    st.markdown(stepper_header_html, unsafe_allow_html=True)

    with st.container(border=True):
        if curr_step == 1:
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin-bottom: 12px;">1. Basic Information</h3>', unsafe_allow_html=True)
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                st.text_input("Full name *", value=user.get("full_name", ""), key="step_fullname")
                st.date_input("Date of birth *", key="step_dob")
                st.selectbox("Gender", ["Female", "Male", "Non-binary", "Prefer to self-describe", "Prefer not to say"], key="step_gender")
                st.selectbox("Blood group", ["Select blood group", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key="step_blood")
            with b_col2:
                st.text_input("Email address *", value=user.get("email", ""), key="step_email")
                st.text_input("Phone number", value="", placeholder="+91 98765 43210", key="step_phone")
                h_col, w_col = st.columns(2)
                with h_col:
                    st.number_input("Height (cm)", min_value=50, max_value=250, value=165, key="step_height")
                with w_col:
                    st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=60.0, key="step_weight")
                st.selectbox("Preferred language *", ["English", "Hindi", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati", "Other"], key="step_lang")

        elif curr_step == 2:
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin-bottom: 12px;">2. Emergency Contact Information</h3>', unsafe_allow_html=True)
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                st.text_input("Emergency contact name *", value="", placeholder="Primary emergency contact", key="step_em_name")
                st.selectbox("Relationship *", ["Spouse", "Parent", "Sibling", "Child", "Guardian", "Friend", "Other"], key="step_em_rel")
            with e_col2:
                st.text_input("Emergency phone number *", value="", placeholder="+91 ...", key="step_em_phone")
                st.text_input("Alternative phone number", value="", placeholder="Optional secondary contact", key="step_em_alt")
            st.checkbox("Emergency contact consent: I authorize MediCare AI to display this contact in emergencies", value=True, key="step_em_consent")

        elif curr_step == 3:
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin-bottom: 12px;">3. Medical History</h3>', unsafe_allow_html=True)
            has_cond = st.radio("Do you have any existing medical conditions?", ["Yes", "No"], horizontal=True, key="step_has_cond")
            if has_cond == "Yes":
                st.multiselect(
                    "Medical condition (select all that apply or add other)",
                    ["Diabetes", "Hypertension", "Heart disease", "Asthma", "Thyroid disorders", "Kidney disease", "Liver disease", "Arthritis", "Epilepsy", "Cancer", "PCOS", "Other"],
                    default=[],
                    key="step_cond_list"
                )
                m_c1, m_c2 = st.columns(2)
                with m_c1:
                    st.date_input("Date of diagnosis", key="step_cond_date")
                    st.selectbox("Current condition status", ["Active", "Managed", "Resolved"], key="step_cond_status")
                with m_c2:
                    st.text_input("Treating doctor's name", value="", placeholder="Doctor name", key="step_doc_name")
                    st.text_input("Hospital or clinic name", value="", placeholder="Clinic / Hospital name", key="step_hosp_name")
            st.markdown("<hr style='border: none; border-top: 1px solid #edf4f7; margin: 12px 0;'>", unsafe_allow_html=True)
            s_c1, s_c2 = st.columns(2)
            with s_c1:
                st.radio("Previous surgeries?", ["No", "Yes"], horizontal=True, key="step_has_surg")
            with s_c2:
                st.radio("Previous hospitalizations?", ["No", "Yes"], horizontal=True, key="step_has_hosp")
            st.text_area("Additional medical history / Family history notes", placeholder="Optional details regarding family health history or previous procedures...", key="step_hist_notes", height=75)

        elif curr_step == 4:
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin-bottom: 12px;">4. Allergies</h3>', unsafe_allow_html=True)
            has_allergy = st.radio("Do you have any known allergies?", ["Yes", "No", "Unknown"], horizontal=True, key="step_has_all")
            if has_allergy == "Yes":
                st.multiselect(
                    "Allergy category",
                    ["Medication allergies", "Food allergies", "Pollen allergies", "Dust allergies", "Insect allergies", "Latex allergies", "Skin allergies", "Other allergies"],
                    default=[],
                    key="step_all_cats"
                )
                a_c1, a_c2 = st.columns(2)
                with a_c1:
                    st.text_input("Specific allergen name (e.g. Penicillin, Peanuts)", value="", placeholder="e.g. Penicillin, Peanuts", key="step_all_name")
                    st.multiselect("Reaction experienced", ["Rash / Hives", "Swelling", "Anaphylaxis", "Breathing difficulty", "Nausea", "Dizziness", "Other"], default=[], key="step_all_react")
                with a_c2:
                    st.selectbox("Severity", ["Mild", "Moderate", "Severe"], index=1, key="step_all_sev")
                    st.date_input("Date identified", key="step_all_date")
                st.caption("Notice: For medication allergies, collect the exact medicine name and reaction rather than just the category.")

        elif curr_step == 5:
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin-bottom: 12px;">5. Current Medications</h3>', unsafe_allow_html=True)
            has_med = st.radio("Are you currently taking medication?", ["Yes", "No"], horizontal=True, key="step_has_med")
            if has_med == "Yes":
                med_c1, med_c2 = st.columns(2)
                with med_c1:
                    st.text_input("Medication name", value="", placeholder="e.g. Metformin", key="step_med_name")
                    st.selectbox("Medication category", ["Inhaler / Respiratory", "Blood pressure", "Antibiotic", "Analgesic", "Endocrine", "Vitamin / Supplement", "Other"], key="step_med_cat")
                    st.text_input("Strength & Prescribed dosage", value="", placeholder="e.g. 500 mg", key="step_med_dose")
                with med_c2:
                    st.selectbox("Frequency", ["Once daily", "Twice daily", "Three times daily", "Weekly", "As prescribed", "Other"], index=0, key="step_med_freq")
                    st.selectbox("Route of administration", ["Oral", "Inhalation", "Sublingual", "Topical", "Subcutaneous", "Other"], index=0, key="step_med_route")
                    st.text_input("Prescribing doctor & reason", value="", placeholder="Prescribing doctor & reason", key="step_med_reason")
            st.caption("Important: These fields record existing prescriptions, not allowing the AI to independently prescribe or modify treatment.")

        elif curr_step == 6:
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin-bottom: 12px;">6. Lifestyle and Health Habits</h3>', unsafe_allow_html=True)
            l_c1, l_c2 = st.columns(2)
            with l_c1:
                st.selectbox("Smoking habits", ["Never", "Former", "Current"], key="step_smk")
                st.selectbox("Alcohol consumption", ["Never", "Occasionally", "Frequently"], key="step_alc")
                st.selectbox("Physical activity level", ["Low", "Moderate", "High"], index=1, key="step_act")
                st.number_input("Average sleep duration (hours)", min_value=3, max_value=14, value=7, key="step_slp_hrs")
                st.selectbox("Sleep quality", ["Good", "Average", "Poor"], key="step_slp_qual")
            with l_c2:
                st.selectbox("Dietary preference", ["Vegetarian", "Vegan", "Non-vegetarian", "Other"], key="step_diet")
                st.number_input("Water intake (litres/day)", min_value=0.5, max_value=8.0, value=2.5, step=0.5, key="step_water")
                st.text_input("Occupation", value="", placeholder="e.g. Software Engineer", key="step_occ")
                st.selectbox("Stress level", ["Low", "Moderate", "High"], index=1, key="step_stress")

        elif curr_step == 7:
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin-bottom: 12px;">7. Health Measurements and Vital Signs</h3>', unsafe_allow_html=True)
            v_c1, v_c2 = st.columns(2)
            with v_c1:
                st.text_input("Blood pressure (mmHg)", value="", placeholder="e.g. 120/80", key="step_bp")
                st.number_input("Heart rate (Beats/minute)", min_value=40, max_value=220, value=72, key="step_hr")
                st.number_input("Body temperature (°C)", min_value=34.0, max_value=42.0, value=36.8, step=0.1, key="step_temp")
            with v_c2:
                st.number_input("Oxygen saturation (% SpO2)", min_value=70, max_value=100, value=98, key="step_spo2")
                st.number_input("Blood glucose (mg/dL)", min_value=40, max_value=500, value=95, key="step_glu")
                st.number_input("Respiratory rate (Breaths/minute)", min_value=8, max_value=50, value=16, key="step_resp")
            st.caption("Clinical context note: Measurements include dates, times, units, and measurement context. Don't automatically treat a single measurement as a diagnosis.")

        elif curr_step == 8:
            st.markdown('<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin-bottom: 12px;">8. Consent, Privacy and Data Authorization</h3>', unsafe_allow_html=True)
            st.markdown('<p style="color: #637d8c; font-size: 0.9rem; margin-bottom: 14px;">Consent should be specific, informed, revocable, and separate from general terms. Optional AI processing is never a condition for general browsing.</p>', unsafe_allow_html=True)
            st.checkbox("Privacy policy acceptance: I acknowledge the MediCare AI data handling policy *", value=True, key="step_c_priv")
            st.checkbox("Terms and conditions acceptance: I accept the platform terms of use *", value=True, key="step_c_terms")
            st.checkbox("Medical information consent: I consent to processing health information for educational clarity *", value=True, key="step_c_med")
            st.checkbox("AI processing consent: I explicitly authorize AI explanations of my records and reports", value=True, key="step_c_ai")
            st.checkbox("Third-party data sharing consent: I understand external AI providers process de-identified clinical terms", value=True, key="step_c_third")
            st.checkbox("Report upload consent: I authorize document parsing and structured lab value extraction", value=True, key="step_c_rep")

        # Step Navigation Buttons
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        col_prev, col_spacer, col_next = st.columns([1, 2.5, 1])
        with col_prev:
            if curr_step > 1:
                st.markdown("<div class='step-nav-btn'>", unsafe_allow_html=True)
                if st.button("← Previous", key="btn_step_prev", use_container_width=True):
                    st.session_state["profile_step"] = curr_step - 1
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        with col_next:
            st.markdown("<div class='step-nav-btn'>", unsafe_allow_html=True)
            if curr_step < 8:
                if st.button("Next →", key="btn_step_next", type="primary", use_container_width=True):
                    st.session_state["profile_step"] = curr_step + 1
                    st.rerun()
            else:
                if st.button("Reset Form ↺", key="btn_step_restart", type="primary", use_container_width=True):
                    st.session_state["profile_step"] = 1
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<p style="text-align: center; color: #8fa5b0; font-size: 0.8rem; margin: 12px 0 0 0;">Your clinical data and privacy preferences are securely maintained.</p>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # CARD 2: DROPZONE & PDF UPLOADER (SECTION 9 IN ACTION)
    # --------------------------------------------------------------------------
    st.markdown(
        '<div style="background: #f7fbfb; border: 1.5px dashed #9fd2c7; border-radius: 20px; padding: 32px 24px; text-align: center; margin-bottom: 1.8rem;">'
        '<div style="width: 44px; height: 44px; border-radius: 12px; background: #eaf6f4; margin: 0 auto 12px auto; display: flex; align-items: center; justify-content: center; color: #087c76;">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#087c76" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
        '<polyline points="14 2 14 8 20 8"></polyline>'
        '<line x1="12" y1="18" x2="12" y2="12"></line>'
        '<line x1="9" y1="15" x2="12" y2="12"></line>'
        '<line x1="15" y1="15" x2="12" y2="12"></line>'
        '</svg>'
        '</div>'
        '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 4px 0;">Drop a PDF here, or choose a file</h2>'
        '<p style="color: #718a97; font-size: 0.85rem; margin: 0 0 18px 0;">PDF only · local preview (Blood tests, Thyroid, Lipid profile, X-ray, Prescriptions)</p>',
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        u_col1, u_col2 = st.columns([0.65, 0.35])
        with u_col1:
            st.markdown(f'<p style="color: #087c76; font-weight: 700; margin: 8px 0; font-size: 0.92rem;">Selected: <strong>{uploaded_file.name}</strong> ({uploaded_file.size / 1024:.1f} KB)</p>', unsafe_allow_html=True)
        with u_col2:
            if st.button("⚡ Extract & Analyze Report", type="primary", use_container_width=True):
                with st.spinner("Extracting parameters via PyMuPDF & analyzing..."):
                    res = api_client.upload_report(
                        file_bytes=uploaded_file.getvalue(),
                        filename=uploaded_file.name,
                        report_title=uploaded_file.name.replace(".pdf", "")
                    )
                    if res.get("success"):
                        st.session_state["analyzed_report"] = res.get("data")
                        st.success("Report successfully analyzed and recorded!")
                        st.rerun()
                    else:
                        st.error(f"Analysis failed: {res.get('message', 'Unable to parse PDF.')}")

    # Fetch live reports list from API
    live_reports = []
    res_list = api_client.get_reports()
    if res_list.get("success") and res_list.get("data"):
        live_reports = res_list["data"]

    # Active report data (either uploaded or latest available)
    active_report = st.session_state.get("analyzed_report")

    # --------------------------------------------------------------------------
    # ROW 3: TWO SURFACE CARDS (Uploaded Reports & Report Summary)
    # --------------------------------------------------------------------------
    col_hist, col_sum = st.columns([1, 1], gap="medium")

    with col_hist:
        reports_card_html = (
            '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; min-height: 205px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
            '<h2 style="font-size: 1.18rem; font-weight: 800; color: #193648; margin: 0 0 16px 0;">Uploaded reports</h2>'
        )
        if live_reports:
            for idx, r in enumerate(live_reports[:4]):
                sep = '<div style="border-bottom: 1px solid #eef3f6; margin: 12px 0;"></div>' if idx > 0 else ''
                status_color = "#087c76" if r.get("status") == "Reviewed" else "#1a6c8e"
                status_bg = "#eaf6f4" if r.get("status") == "Reviewed" else "#e8f2f8"
                date_str = str(r.get("uploaded_at", ""))[:10]
                reports_card_html += (
                    f'{sep}'
                    '<div style="display: flex; justify-content: space-between; align-items: center;">'
                    '<div>'
                    f'<strong style="font-size: 0.94rem; color: #193648; display: block;">{r.get("file_name", "Report.pdf")}</strong>'
                    f'<span style="color: #718a97; font-size: 0.82rem;">{date_str}</span>'
                    '</div>'
                    f'<span style="background: {status_bg}; color: {status_color}; padding: 4px 14px; border-radius: 16px; font-size: 0.8rem; font-weight: 700;">{r.get("status", "Available")}</span>'
                    '</div>'
                )
        else:
            reports_card_html += (
                '<div style="text-align: center; padding: 32px 14px; color: #718a97;">'
                '<div style="font-size: 1.8rem; margin-bottom: 8px;">📄</div>'
                '<strong style="display: block; color: #193648; font-size: 0.95rem; margin-bottom: 4px;">No reports uploaded yet</strong>'
                '<span style="font-size: 0.84rem;">Upload your diagnostic lab PDF above to analyze values.</span>'
                '</div>'
            )
        reports_card_html += '</div>'
        st.markdown(reports_card_html, unsafe_allow_html=True)

    with col_sum:
        if active_report:
            summary_text = active_report.get("ai_summary", "Diagnostic report analyzed.")
            has_badge = True
        elif live_reports:
            summary_text = live_reports[0].get("ai_summary", "Upload or select a report to see an AI clinical explanation.")
            has_badge = True
        else:
            summary_text = "Upload a diagnostic lab report or consultation document above to receive a structured educational summary and personalized questions for your doctor."
            has_badge = False

        points_html = ""
        if active_report and active_report.get("doctor_discussion_points"):
            pt_items = "".join([f"<li style='margin-bottom: 4px;'>{p}</li>" for p in active_report["doctor_discussion_points"][:3]])
            points_html = f"<div style='margin-top: 10px; font-size: 0.84rem; color: #155c73;'><strong>Questions for your doctor:</strong><ul style='padding-left: 18px; margin-top: 4px;'>{pt_items}</ul></div>"

        badges_html = (
            '<div style="display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap;">'
            '<span style="background: #eaf6f4; color: #087c76; padding: 5px 14px; border-radius: 16px; font-size: 0.78rem; font-weight: 700;">Source: PDF extracted</span>'
            '<span style="background: #e8f2f8; color: #1a6c8e; padding: 5px 14px; border-radius: 16px; font-size: 0.78rem; font-weight: 700;">AI: educational context</span>'
            '</div>'
        ) if has_badge else ''

        summary_card_html = (
            '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; min-height: 205px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); display: flex; flex-direction: column; justify-content: space-between;">'
            '<div>'
            '<h2 style="font-size: 1.18rem; font-weight: 800; color: #193648; margin: 0 0 10px 0;">AI Educational Summary</h2>'
            f'<p style="color: #637d8c; font-size: 0.88rem; line-height: 1.6; margin: 0;">{summary_text}</p>'
            f'{points_html}'
            '</div>'
            f'{badges_html}'
            '</div>'
        )
        st.markdown(summary_card_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 4: LABORATORY RESULTS TABLE
    # --------------------------------------------------------------------------
    params_to_show = (
        active_report.get("parsed_parameters") if active_report and active_report.get("parsed_parameters")
        else (live_reports[0].get("parsed_parameters") if live_reports and live_reports[0].get("parsed_parameters") else [])
    )

    if not params_to_show:
        table_card_html = (
            '<div style="background: #FFFFFF; border: 1.5px dashed #b9d8d5; border-radius: 20px; padding: 36px 24px; text-align: center; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); margin-bottom: 1.8rem;">'
            '<div style="font-size: 2rem; margin-bottom: 8px;">📊</div>'
            '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 6px 0;">Laboratory results</h2>'
            '<p style="color: #637d8c; font-size: 0.92rem; margin: 0;">No test parameters extracted yet. Upload a diagnostic PDF medical report above to view structured biomarker values.</p>'
            '</div>'
        )
        st.markdown(table_card_html, unsafe_allow_html=True)
    else:
        table_rows = ""
        for p in params_to_show:
            status_val = p.get("status", "Normal")
            if status_val == "Elevated":
                badge_html = '<span style="background: #fdf2e9; color: #b75e18; padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 0.78rem;">Elevated</span>'
            elif status_val == "Low":
                badge_html = '<span style="background: #eef2fa; color: #2e5aac; padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 0.78rem;">Low</span>'
            else:
                badge_html = '<span style="background: #eaf6f4; color: #087c76; padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 0.78rem;">Normal</span>'

            table_rows += (
                '<tr style="border-bottom: 1px solid #f0f4f7;">'
                f'<td style="padding: 14px; font-weight: 600; color: #193648;">{p.get("test_name", "Test")}</td>'
                f'<td style="padding: 14px; font-weight: 800; color: #193648;">{p.get("observed_value", "—")}</td>'
                f'<td style="padding: 14px; color: #637d8c;">{p.get("reference_range", "Standard")}</td>'
                f'<td style="padding: 14px; color: #637d8c;">{p.get("unit", "")}</td>'
                f'<td style="padding: 14px;">{badge_html}</td>'
                f'<td style="padding: 14px; color: #087c76; font-size: 0.85rem;">{p.get("explanation", "")}</td>'
                '</tr>'
            )

        table_card_html = (
            '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); margin-bottom: 1.8rem; overflow-x: auto;">'
            '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 20px 0;">Laboratory results</h2>'
            '<table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">'
            '<thead>'
            '<tr style="border-bottom: 1px solid #eef3f6; color: #4a6873;">'
            '<th style="padding: 12px 14px; font-weight: 700; font-size: 0.88rem;">Test</th>'
            '<th style="padding: 12px 14px; font-weight: 700; font-size: 0.88rem;">Extracted value</th>'
            '<th style="padding: 12px 14px; font-weight: 700; font-size: 0.88rem;">Reference range</th>'
            '<th style="padding: 12px 14px; font-weight: 700; font-size: 0.88rem;">Unit</th>'
            '<th style="padding: 12px 14px; font-weight: 700; font-size: 0.88rem;">Status</th>'
            '<th style="padding: 12px 14px; font-weight: 700; font-size: 0.88rem;">AI-generated explanation · not a diagnosis</th>'
            '</tr>'
            '</thead>'
            f'<tbody>{table_rows}</tbody>'
            '</table>'
            '</div>'
        )
        st.markdown(table_card_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 5: TERM EXPLAINERS (Two Equal Cards)
    # --------------------------------------------------------------------------
    t_col1, t_col2 = st.columns([1, 1], gap="medium")

    with t_col1:
        term1_html = (
            '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; min-height: 145px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
            '<span style="background: #eaf3f8; color: #18698c; font-size: 0.74rem; font-weight: 800; padding: 4px 12px; border-radius: 20px; letter-spacing: 0.06em; text-transform: uppercase;">TERM EXPLAINER · AI</span>'
            '<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin: 12px 0 6px 0;">Reference interval</h3>'
            '<p style="color: #637d8c; font-size: 0.9rem; line-height: 1.6; margin: 0;">A comparison range supplied by a laboratory. It is not a personal diagnosis.</p>'
            '</div>'
        )
        st.markdown(term1_html, unsafe_allow_html=True)

    with t_col2:
        term2_html = (
            '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; min-height: 145px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
            '<span style="background: #eaf3f8; color: #18698c; font-size: 0.74rem; font-weight: 800; padding: 4px 12px; border-radius: 20px; letter-spacing: 0.06em; text-transform: uppercase;">TERM EXPLAINER · AI</span>'
            '<h3 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin: 12px 0 6px 0;">Biomarker</h3>'
            '<p style="color: #637d8c; font-size: 0.9rem; line-height: 1.6; margin: 0;">A measurable characteristic that can help inform a broader clinical assessment.</p>'
            '</div>'
        )
        st.markdown(term2_html, unsafe_allow_html=True)

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
