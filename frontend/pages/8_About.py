import streamlit as st
import os
import sys

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_client import api_client

# Configure page settings
st.set_page_config(
    page_title="About Us | MediCare AI",
    page_icon="ℹ️",
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

# Page-specific button styling for About page
st.markdown(
    """
    <style>
    div[data-testid="stButton"] button {
        background: #176a9a !important;
        background-color: #176a9a !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.75rem 1.6rem !important;
    }
    div[data-testid="stButton"] button *,
    div[data-testid="stButton"] button p,
    div[data-testid="stButton"] button span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        font-family: 'Manrope', sans-serif !important;
    }
    div[data-testid="stButton"] button:hover {
        background: #12557d !important;
        background-color: #12557d !important;
    }
    div[data-testid="stButton"] button:hover * {
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
    '<a href="/About" target="_self" class="canva-nav-link active" style="color: #076c70; background-color: #dff2f1;">About</a>'
    '<a href="/Contact" target="_self" class="canva-nav-link">Contact</a>'
    '</div>'
    f'{auth_nav_right}'
    '</div>'
    '</div>'
)
st.markdown(top_navbar_html, unsafe_allow_html=True)

# ==============================================================================
# HERO SECTION (Two-Column Layout: Text Left | Doctor Working Photo Right)
# ==============================================================================
col_left, col_right = st.columns([1.1, 0.9], gap="large")

with col_left:
    st.markdown(
        """
        <span class="eyebrow" style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">ABOUT MEDICARE AI</span>
        <h1 style="font-size: 2.15rem; font-weight: 800; color: #193648; margin: 0.35rem 0 0.85rem 0; line-height: 1.18; letter-spacing: -0.02em;">
            A little more clarity can make a big difference.
        </h1>
        <p class="muted" style="font-size: 1.05rem; line-height: 1.65; margin-bottom: 2rem; color: #637d8c;">
            MediCare AI is a concept for a calmer, more understandable healthcare information experience—bringing general-purpose educational assistance and everyday organization into one thoughtful workspace.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    col_btn, _ = st.columns([1, 1.2])
    with col_btn:
        if st.button("Explore the assistant", key="about_explore_btn", type="primary", use_container_width=True):
            st.switch_page("pages/2_AI_Chatbot.py")

with col_right:
    st.markdown(
        """
        <div style="border-radius: 28px; overflow: hidden; box-shadow: 0 16px 45px rgba(24, 75, 103, 0.08); height: 380px;">
            <img src="https://images.pexels.com/photos/8376232/pexels-photo-8376232.jpeg?auto=compress&cs=tinysrgb&w=1280" 
                 alt="Healthcare clinician working on a laptop at medical workstation" 
                 style="width: 100%; height: 380px; object-fit: cover; display: block; border-radius: 28px;" />
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 3.5rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# MISSION AND VISION SECTION (Two Equal Canva Surface Cards)
# ==============================================================================
col_m, col_v = st.columns(2, gap="large")

with col_m:
    st.markdown(
        """
        <div class="surface" style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 24px; padding: 2.2rem 2.4rem; box-shadow: 0 12px 40px rgba(24, 75, 103, 0.04); height: 100%;">
            <span class="eyebrow" style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">OUR MISSION</span>
            <h3 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0.5rem 0 0.5rem 0; letter-spacing: -0.01em;">Make information feel understandable.</h3>
            <p class="muted" style="font-size: 0.95rem; line-height: 1.6; margin: 0; color: #637d8c;">
                Help people prepare better questions and navigate general health topics with clarity and confidence.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_v:
    st.markdown(
        """
        <div class="surface" style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 24px; padding: 2.2rem 2.4rem; box-shadow: 0 12px 40px rgba(24, 75, 103, 0.04); height: 100%;">
            <span class="eyebrow" style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">OUR VISION</span>
            <h3 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0.5rem 0 0.5rem 0; letter-spacing: -0.01em;">Support more informed conversations.</h3>
            <p class="muted" style="font-size: 0.95rem; line-height: 1.6; margin: 0; color: #637d8c;">
                Build technology that complements, rather than replaces, relationships with healthcare professionals.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# WHAT THE EXPERIENCE BRINGS TOGETHER (Canva Matrix Card)
# ==============================================================================
st.markdown(
    """
    <div class="surface" style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 24px; padding: 2rem 2.4rem; box-shadow: 0 12px 40px rgba(24, 75, 103, 0.04);">
        <h3 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 1.4rem 0;">What the experience brings together</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; font-size: 0.95rem; font-weight: 600; color: #193648;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #193648; font-size: 0.85rem;">✦</span>
                <span>Educational AI chat</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #193648; font-size: 0.85rem;">▤</span>
                <span>Report terminology</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #193648; font-size: 0.85rem;">⏱</span>
                <span>Medication organization</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #193648; font-size: 0.85rem;">▦</span>
                <span>Appointment planning</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# AMBER HEALTHCARE INFORMATION DISCLAIMER BANNER
# ==============================================================================
st.markdown(
    """
    <div style="background: #fff8e9; border: 1px solid #fae6be; color: #74531a; border-radius: 12px; padding: 14px 22px; font-size: 0.85rem; margin-top: 1.8rem; font-weight: 500; line-height: 1.5;">
        Healthcare information disclaimer: AI explanations are educational and non-diagnostic. Always seek advice from a qualified healthcare professional for individual concerns.
    </div>
    """,
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
