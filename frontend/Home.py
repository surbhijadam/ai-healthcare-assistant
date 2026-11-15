import streamlit as st
import streamlit.components.v1 as components
import os
import sys

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from api_client import api_client

# Configure page settings
st.set_page_config(
    page_title="MediCare AI — Intelligent Healthcare Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Canva-aligned CSS custom stylesheet
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Synchronize persistent session state so logins survive full page navigation
api_client.sync_session_state()

# ==============================================================================
# JAVASCRIPT SMOOTH SCROLL HANDLER (Ensures Instant Smooth Scroll to #features)
# ==============================================================================
components.html(
    """
    <script>
    (function() {
        function scrollToFeatures() {
            try {
                const doc = window.parent.document;
                const target = doc.getElementById('features');
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            } catch(e) {}
        }

        function bindTriggers() {
            try {
                const doc = window.parent.document;
                const triggers = doc.querySelectorAll('a[href="#features"], a[href$="#features"]');
                triggers.forEach(el => {
                    if (!el.dataset.smoothBound) {
                        el.dataset.smoothBound = "true";
                        el.addEventListener('click', function(ev) {
                            ev.preventDefault();
                            scrollToFeatures();
                            try {
                                window.parent.history.pushState(null, null, '#features');
                            } catch(e) {}
                        });
                    }
                });

                if (window.parent.location.hash === '#features') {
                    setTimeout(scrollToFeatures, 250);
                }
            } catch(e) {}
        }

        bindTriggers();
        setTimeout(bindTriggers, 300);
        setTimeout(bindTriggers, 800);
        setTimeout(bindTriggers, 1500);
    })();
    </script>
    """,
    height=0,
    width=0
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
    '<div style="background: #FFFFFF; border-bottom: 1px solid #dce9ef; padding: 12px 24px; border-radius: 16px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
    '<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">'
    '<div style="display: flex; align-items: center; gap: 10px;">'
    '<span class="iconbox" style="margin: 0; width: 38px; height: 38px; font-size: 1.15rem; background: #e8f6f3; color: #087c76;">🩺</span>'
    '<span style="color: #155c73; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;">MediCare AI</span>'
    '</div>'
    '<div style="display: flex; align-items: center; gap: 14px; font-weight: 700; font-size: 0.92rem;">'
    '<a href="#" target="_self" class="canva-nav-link active">Home</a>'
    '<a href="#features" target="_self" class="canva-nav-link">Features</a>'
    '<a href="/Dashboard" target="_self" class="canva-nav-link">Dashboard</a>'
    '<a href="/About" target="_self" class="canva-nav-link">About</a>'
    '<a href="/Contact" target="_self" class="canva-nav-link">Contact</a>'
    '</div>'
    f'{auth_nav_right}'
    '</div>'
    '</div>'
)
st.markdown(top_navbar_html, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# HERO SECTION (100% Canva Matching: Large Typography + Clinical Photo + Float Card)
# ==============================================================================
col_hero_text, col_hero_art = st.columns([1.1, 0.9], gap="large")

with col_hero_text:
    st.markdown('<span class="eyebrow">A MORE HUMAN WAY TO UNDERSTAND HEALTH</span>', unsafe_allow_html=True)
    st.markdown(
        """
        <h1 style="font-size: clamp(2.6rem, 4.5vw, 4.2rem); line-height: 1.08; font-weight: 800; color: #193648; margin-top: 0.4rem; margin-bottom: 1.4rem; letter-spacing: -0.04em;">
            Your Health,<br/>Smarter with AI.
        </h1>
        <p class="muted" style="font-size: 1.12rem; line-height: 1.65; margin-bottom: 1.8rem; max-width: 580px;">
            Meet your AI-powered healthcare assistant: explore everyday health questions, make sense of medical terms, and keep important information organized in one calm space.
        </p>
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 1.4rem; flex-wrap: wrap;">
            <a href="/Login_Register?mode=register" target="_self" class="canva-btn-primary" style="padding: 11px 26px; font-size: 0.95rem; font-weight: 800; text-decoration: none; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center;">
                Get Started
            </a>
            <a href="#features" target="_self" class="canva-btn-secondary" style="padding: 11px 26px; font-size: 0.95rem; font-weight: 800; text-decoration: none; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center;">
                Explore Features
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="tiny muted" style="margin-top: 1rem;">Designed for information and organization. Never a substitute for professional care.</p>',
        unsafe_allow_html=True
    )

with col_hero_art:
    # Exact Canva Clinical Doctor Image with Floating Clarity Card
    st.markdown(
        """
        <div style="position: relative; border-radius: 28px; overflow: hidden; box-shadow: 0 16px 45px rgba(24, 75, 103, 0.08); min-height: 380px;">
            <img src="https://images.pexels.com/photos/7578803/pexels-photo-7578803.jpeg?auto=compress&cs=tinysrgb&w=1280" 
                 alt="Healthcare professional in modern clinical setting" 
                 style="width: 100%; height: 380px; object-fit: cover; display: block; border-radius: 28px;" />
            <div style="position: absolute; bottom: 20px; left: 20px; background: #FFFFFF; box-shadow: 0 10px 30px rgba(22, 70, 88, 0.22); border-radius: 16px; padding: 12px 18px; display: inline-flex; align-items: center; gap: 12px; border: 1px solid #dce9ef;">
                <span class="iconbox" style="margin: 0; width: 36px; height: 36px; background: #e8f6f3; color: #087c76; font-size: 1.1rem;">✨</span>
                <div>
                    <strong style="font-size: 0.92rem; color: #193648; display: block;">AI-powered clarity</strong>
                    <small class="muted" style="font-size: 0.78rem;">Designed to support, not diagnose</small>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 4.5rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# ONE CONNECTED EXPERIENCE (4 Canva Feature Cards)
# ==============================================================================
st.markdown("<div id='features' style='scroll-margin-top: 2rem;'></div>", unsafe_allow_html=True)
st.markdown('<span class="eyebrow">ONE CONNECTED EXPERIENCE</span>', unsafe_allow_html=True)
st.markdown('<h2 style="font-size: 2.1rem; font-weight: 800; margin-top: 0.2rem; margin-bottom: 2rem; color: #193648;">Carefully designed around your questions.</h2>', unsafe_allow_html=True)

f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
    st.markdown(
        """
        <div class="feature-card-uniform">
            <span class="feature-card-icon">💬</span>
            <h3 class="feature-card-title">AI Chatbot</h3>
            <p class="feature-card-desc">
                Explore general health topics in a warm, easy-to-follow conversation.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Explore chat →", key="feat_chat_btn", use_container_width=True):
        st.switch_page("pages/2_AI_Chatbot.py")

with f_col2:
    st.markdown(
        """
        <div class="feature-card-uniform">
            <span class="feature-card-icon">📄</span>
            <h3 class="feature-card-title">Medical Report Assistant</h3>
            <p class="feature-card-desc">
                See how report values and educational explanations can be clearly distinguished.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("View reports →", key="feat_reports_btn", use_container_width=True):
        st.switch_page("pages/3_Medical_Reports.py")

with f_col3:
    st.markdown(
        """
        <div class="feature-card-uniform">
            <span class="feature-card-icon">💊</span>
            <h3 class="feature-card-title">Medication Manager</h3>
            <p class="feature-card-desc">
                Keep a simple view of schedules and user-marked dose activity.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("View manager →", key="feat_meds_btn", use_container_width=True):
        st.switch_page("pages/4_Medications.py")

with f_col4:
    st.markdown(
        """
        <div class="feature-card-uniform">
            <span class="feature-card-icon">🗓️</span>
            <h3 class="feature-card-title">Appointment Manager</h3>
            <p class="feature-card-desc">
                See your visits, dates, and appointment details at a glance.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("View calendar →", key="feat_appts_btn", use_container_width=True):
        st.switch_page("pages/5_Appointments.py")

st.markdown("<div style='margin-top: 4.5rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# HOW IT WORKS (Full-width Mint Background Band #e9f5f4)
# ==============================================================================
st.markdown(
    """
    <div style="background: #e9f5f4; border-radius: 28px; padding: 3rem 2.5rem; margin-bottom: 4rem;">
        <span class="eyebrow" style="color: #087c76 !important;">HOW IT WORKS</span>
        <h2 style="font-size: 2rem; font-weight: 800; margin-top: 0.3rem; margin-bottom: 2rem; color: #193648;">
            A clearer path to everyday health information
        </h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            <div class="surface" style="margin-bottom: 0; padding: 1.8rem;">
                <span class="badge" style="background: #e4f5ee; color: #167053;">01 · ASK</span>
                <h3 style="font-size: 1.15rem; font-weight: 800; margin-top: 1.2rem; margin-bottom: 0.5rem; color: #193648;">Start a conversation</h3>
                <p class="muted text-sm" style="margin: 0; line-height: 1.5;">
                    Ask a question in plain language.
                </p>
            </div>
            <div class="surface" style="margin-bottom: 0; padding: 1.8rem;">
                <span class="badge" style="background: #e4f5ee; color: #167053;">02 · ORGANIZE</span>
                <h3 style="font-size: 1.15rem; font-weight: 800; margin-top: 1.2rem; margin-bottom: 0.5rem; color: #193648;">Bring your information together</h3>
                <p class="muted text-sm" style="margin: 0; line-height: 1.5;">
                    Preview reports, schedules, and visits in one place.
                </p>
            </div>
            <div class="surface" style="margin-bottom: 0; padding: 1.8rem;">
                <span class="badge" style="background: #e4f5ee; color: #167053;">03 · DISCUSS</span>
                <h3 style="font-size: 1.15rem; font-weight: 800; margin-top: 1.2rem; margin-bottom: 0.5rem; color: #193648;">Talk with your clinician</h3>
                <p class="muted text-sm" style="margin: 0; line-height: 1.5;">
                    Use clearer questions to guide professional conversations.
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# WHY CHOOSE US
# ==============================================================================
wc_left, wc_right = st.columns([1.1, 0.9], gap="large")

with wc_left:
    st.markdown('<span class="eyebrow">WHY CHOOSE US</span>', unsafe_allow_html=True)
    st.markdown(
        """
        <h2 style="font-size: 2.1rem; font-weight: 800; margin-top: 0.3rem; color: #193648; line-height: 1.2;">
            Thoughtful technology,<br/>human-first care.
        </h2>
        <p class="muted" style="line-height: 1.7; font-size: 1.05rem; margin-top: 1.2rem; max-width: 520px;">
            A calm workspace makes complicated information easier to navigate. 
            Clear labels separate source information from AI-generated educational explanations.
        </p>
        """,
        unsafe_allow_html=True
    )

with wc_right:
    st.markdown(
        """
        <div class="surface" style="padding: 1.8rem; margin-bottom: 1rem;">
            <div style="display: flex; gap: 16px; align-items: flex-start; margin-bottom: 1.2rem;">
                <span class="iconbox" style="margin: 0; background: #e8f6f3; color: #087c76;">🛡️</span>
                <div>
                    <strong style="font-size: 1.05rem; color: #193648; display: block;">Safety by design</strong>
                    <p class="muted text-sm" style="margin: 4px 0 0 0; line-height: 1.5;">
                        Information is framed as education, never a diagnosis.
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 16px; align-items: flex-start;">
                <span class="iconbox" style="margin: 0; background: #e8f6f3; color: #087c76;">🗂️</span>
                <div>
                    <strong style="font-size: 1.05rem; color: #193648; display: block;">Everything in context</strong>
                    <p class="muted text-sm" style="margin: 4px 0 0 0; line-height: 1.5;">
                        Conversations, records, and visits are easy to find.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# BOTTOM HEALTHCARE SAFETY DISCLAIMER (Exact Canva Placement - Single Line)
# ==============================================================================
st.markdown(
    """
    <p class="muted" style="text-align: center; margin: 2.2rem auto 1.5rem auto; width: 100%; max-width: 100%; font-size: clamp(0.74rem, 0.95vw, 0.86rem); white-space: nowrap; line-height: 1.5;">
        Healthcare safety: This experience offers general educational information only. It cannot diagnose, prescribe, or replace advice from a qualified healthcare professional.
    </p>
    """,
    unsafe_allow_html=True
)

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
