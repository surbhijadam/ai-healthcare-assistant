import streamlit as st
import os
import sys

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_client import api_client

# Configure page settings
st.set_page_config(
    page_title="Contact Us | MediCare AI",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Synchronize persistent session state so logins survive full page navigation
api_client.sync_session_state()

# Load Canva-aligned CSS custom stylesheet
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page-specific styling for the Canva Contact cards and Form
st.markdown(
    """
    <style>
    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #dce9ef !important;
        border-radius: 28px !important;
        padding: 2.4rem 2.6rem !important;
        box-shadow: 0 16px 45px rgba(24, 75, 103, 0.055) !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stForm"] label {
        font-weight: 700 !important;
        color: #193648 !important;
        font-size: 0.92rem !important;
        margin-bottom: 4px !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        background: #176a9a !important;
        background-color: #176a9a !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.7rem 1.8rem !important;
    }
    div[data-testid="stFormSubmitButton"] button *,
    div[data-testid="stFormSubmitButton"] button p,
    div[data-testid="stFormSubmitButton"] button span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        font-family: 'Manrope', sans-serif !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: #12557d !important;
        background-color: #12557d !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover * {
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# TOP NAVBAR (100% Canva Layout: Logo Left | Menu Center | Auth Right)
# ==============================================================================
is_auth = st.session_state.get("authenticated", False)
user = st.session_state.get("user")
if is_auth and user:
    first_name = user.get("full_name", "User").split()[0]
    initials = "".join([p[0] for p in user.get("full_name", "U").split()[:2]]).upper() or "U"
    auth_nav_right = (
        f'<div style="display: flex; align-items: center; gap: 10px;">'
        f'<span style="color: #155c73; font-weight: 700; font-size: 0.88rem;">{first_name}</span>'
        f'<div style="width: 32px; height: 32px; border-radius: 50%; background: #d5eee9; color: #08675f; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem;">{initials}</div>'
        f'<a href="/Profile" target="_self" class="canva-nav-link" style="color: #547382; font-size: 0.86rem;">Profile</a>'
        f'</div>'
    )
else:
    auth_nav_right = (
        '<div style="display: flex; align-items: center; gap: 10px;">'
        '<a href="/Login_Register?mode=login" target="_self" class="canva-nav-link" style="color: #547382;">Login</a>'
        '<a href="/Login_Register?mode=register" target="_self" class="canva-btn-primary" style="padding: 7px 18px; font-size: 0.88rem; text-decoration: none; border-radius: 10px;">Get Started</a>'
        '</div>'
    )

top_navbar_html = (
    '<div style="background: #FFFFFF; border-bottom: 1px solid #dce9ef; padding: 12px 24px; border-radius: 16px; margin-bottom: 2.5rem; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
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
    '<a href="/Contact" target="_self" class="canva-nav-link active" style="color: #076c70; background-color: #dff2f1;">Contact</a>'
    '</div>'
    f'{auth_nav_right}'
    '</div>'
    '</div>'
)
st.markdown(top_navbar_html, unsafe_allow_html=True)

# ==============================================================================
# PAGE HEADER SECTION (Canva Eyebrow + Large Title + Subtitle)
# ==============================================================================
st.markdown(
    """
    <span class="eyebrow" style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">WE'RE HERE TO HELP</span>
    <h1 style="font-size: 2.1rem; font-weight: 800; color: #193648; margin: 0.3rem 0 0.35rem 0; letter-spacing: -0.02em;">Let's start a conversation.</h1>
    <p class="muted" style="font-size: 0.95rem; margin: 0 0 2rem 0;">Have a question about the experience? Send our team a message.</p>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# UPPER SECTION: TWO-COLUMN LAYOUT (Send a message Form Left | Support Card Right)
# ==============================================================================
col_form, col_info = st.columns([1.75, 1], gap="large")

with col_form:
    with st.form("canva_contact_form", border=False):
        st.markdown('<h2 style="font-size: 1.35rem; font-weight: 800; color: #193648; margin: 0 0 1.4rem 0;">Send a message</h2>', unsafe_allow_html=True)
        
        c_n, c_e = st.columns(2)
        with c_n:
            name = st.text_input("Name", placeholder="Your name")
        with c_e:
            email = st.text_input("Email", placeholder="you@example.com")
            
        subject = st.text_input("Subject", placeholder="How can we help?")
        message = st.text_area("Message", placeholder="Tell us a little more", height=130)
        
        btn_col, _ = st.columns([1, 2.5])
        with btn_col:
            submitted = st.form_submit_button("Send message", type="primary", use_container_width=True)
            
        st.markdown(
            """
            <p class="muted" style="font-size: 0.8rem; margin-top: 1.2rem; margin-bottom: 0; line-height: 1.5;">
                Please do not include sensitive medical details. For urgent care, contact local emergency services.
            </p>
            """,
            unsafe_allow_html=True
        )
        
        if submitted:
            if not name or not email or not message:
                st.error("Please complete all required fields before sending.")
            else:
                st.success("Thank you for your message! Our team will get back to you shortly.")

with col_info:
    st.markdown(
        """
        <div class="surface" style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 28px; padding: 2.2rem 2rem; box-shadow: 0 16px 45px rgba(24, 75, 103, 0.055);">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: #e8f6f3; color: #087c76; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 1.2rem;">
                ✉️
            </div>
            <h3 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 0.35rem 0;">Contact & support</h3>
            <p class="muted" style="font-size: 0.92rem; margin: 0 0 0.75rem 0;">Product enquiries and general support</p>
            <a href="mailto:hello@medicareai.example" style="color: #087c76; font-weight: 800; font-size: 0.95rem; text-decoration: none;">
                hello@medicareai.example
            </a>
            <p class="muted" style="font-size: 0.82rem; margin-top: 1.8rem; margin-bottom: 0; line-height: 1.55;">
                Get in touch with our healthcare support team. Use the form to submit an enquiry.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# LOWER SECTION: FREQUENTLY ASKED QUESTIONS (Interactive Dropdown Accordions)
# ==============================================================================
st.markdown(
    """<div class="surface" style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 28px; padding: 2.4rem 2.8rem; box-shadow: 0 16px 45px rgba(24, 75, 103, 0.055);">
<h2 style="font-size: 1.35rem; font-weight: 800; color: #193648; margin: 0 0 1.2rem 0;">Frequently asked questions</h2>
<details class="faq-item" open>
<summary>
<span>Can the assistant diagnose a condition?</span>
<span class="faq-chevron">⌄</span>
</summary>
<p>
No. It provides general educational information, not diagnoses or personalized medical advice.
</p>
</details>
<details class="faq-item">
<summary>
<span>How are uploaded reports analyzed?</span>
<span class="faq-chevron">⌄</span>
</summary>
<p>
Reports are securely parsed with PyMuPDF and processed with clinical LLM guardrails to extract biomarkers and educational context.
</p>
</details>
<details class="faq-item">
<summary>
<span>Where do contact messages go?</span>
<span class="faq-chevron">⌄</span>
</summary>
<p>
Submitted messages are received directly by the MediCare AI operations and clinical support team.
</p>
</details>
</div>""",
    unsafe_allow_html=True
)

st.markdown("<div style='margin-top: 4.5rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# CANVA DARK FOOTER (#193c4c)
# ==============================================================================
st.markdown(
    """
    <div class="canva-footer" style="background: #193c4c; color: #FFFFFF; border-radius: 20px; padding: 2.5rem 2.2rem; margin-top: 2rem;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 28px;">
            <div>
                <strong style="font-size: 1.25rem; display: flex; align-items: center; gap: 8px; color: #FFFFFF;">
                    ✚ MediCare AI
                </strong>
                <p style="color: #FFFFFF !important; font-size: 0.88rem; margin-top: 10px; line-height: 1.6;">
                    A more understandable way to explore everyday health information.
                </p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.88rem; color: #FFFFFF;">
                <span style="font-weight: 700; color: #FFFFFF;">Navigation</span>
                <span style="color: #FFFFFF;">Home &nbsp;·&nbsp; Features &nbsp;·&nbsp; About &nbsp;·&nbsp; Contact &nbsp;·&nbsp; Dashboard</span>
            </div>
            <div style="font-size: 0.86rem; color: #FFFFFF;">
                <p style="color: #FFFFFF !important; margin: 0 0 6px 0;">hello@medicareai.example</p>
                <p style="color: #FFFFFF !important; margin: 0 0 6px 0;">Educational information only. Not medical advice.</p>
                <p style="color: #FFFFFF !important; margin: 0 0 6px 0;">© 2026 MediCare AI · All rights reserved</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
