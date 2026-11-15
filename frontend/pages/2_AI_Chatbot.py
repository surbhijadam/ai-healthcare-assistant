import streamlit as st
import os
import sys

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_client import api_client
from components.auth_guard import require_auth

# Configure page settings
st.set_page_config(
    page_title="Healthcare Assistant | MediCare AI",
    page_icon="💬",
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

/* Prompt chip buttons styling */
.prompt-chip-btn button {
    background: #eaf6f7 !important;
    background-color: #eaf6f7 !important;
    color: #0e5f73 !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.75rem 1rem !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
}

.prompt-chip-btn button *,
.prompt-chip-btn button p,
.prompt-chip-btn button span {
    color: #0e5f73 !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

.prompt-chip-btn button:hover {
    background: #ddf0f3 !important;
    background-color: #ddf0f3 !important;
    transform: translateY(-1px) !important;
}

.prompt-chip-btn button:hover * {
    color: #084958 !important;
}

</style>""",
    unsafe_allow_html=True
)

# Enforce authentication: only authenticated users can access the AI companion
user = require_auth(page_title="AI Healthcare Assistant")
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

# Initialize default chat session history matching Canva design
if "canva_chat_log" not in st.session_state:
    st.session_state["canva_chat_log"] = [
        {
            "role": "assistant",
            "content": f"Hi {first_name}! I can help explain medical terms, symptoms, and laboratory values in clear everyday language. What would you like to explore?"
        }
    ]

if "active_convo_id" not in st.session_state:
    st.session_state["active_convo_id"] = None


def handle_send_message(query_text: str):
    """Processes user message submission via backend API with emergency guardrails."""
    q = query_text.strip()
    if not q:
        return

    st.session_state["canva_chat_log"].append({"role": "user", "content": q})
    curr_convo_id = st.session_state.get("active_convo_id")

    with st.spinner("Formulating clinical educational response..."):
        res = api_client.chat_query(query=q, conversation_id=curr_convo_id)

    if res.get("success") or res.get("data"):
        data = res.get("data", {})
        answer = data.get("answer", "")
        is_emerg = data.get("emergency_intercepted", False)
        sources = data.get("sources_cited", [])
        if data.get("conversation_id"):
            st.session_state["active_convo_id"] = data["conversation_id"]

        st.session_state["canva_chat_log"].append({
            "role": "assistant",
            "content": answer,
            "emergency": is_emerg,
            "sources": sources
        })
    elif res.get("offline"):
        # Resilient offline educational fallback
        q_l = q.lower()
        if any(kw in q_l for kw in ["chest pain", "shortness of breath", "heart attack", "stroke", "can't breathe"]):
            st.session_state["canva_chat_log"].append({
                "role": "assistant",
                "content": (
                    "🚨 **CRITICAL MEDICAL EMERGENCY DETECTED**\n\n"
                    "Your symptoms indicate a possible acute emergency. Please **call 112 (India) or 911 (US)** or proceed to the nearest emergency room immediately. Do not rely on automated tools."
                ),
                "emergency": True
            })
        elif "cholesterol" in q_l or "ldl" in q_l:
            st.session_state["canva_chat_log"].append({
                "role": "assistant",
                "content": (
                    "**Understanding LDL Cholesterol:**\n\n"
                    "Low-Density Lipoprotein (LDL) carries cholesterol particles through your body. Clinical guidelines generally recommend levels below 100 mg/dL for optimal cardiovascular health.\n\n"
                    "---\n*Notice: Educational information only. Not a medical diagnosis.*"
                ),
                "emergency": False
            })
        else:
            st.session_state["canva_chat_log"].append({
                "role": "assistant",
                "content": (
                    f"In general clinical references, questions regarding '{q[:45]}' are assessed in connection with your overall personal medical background.\n\n"
                    "---\n*Notice: Educational information only. Not a medical diagnosis.*"
                ),
                "emergency": False
            })
    else:
        st.session_state["canva_chat_log"].append({
            "role": "assistant",
            "content": f"⚠️ Notice: {res.get('message', 'Unable to reach assistant.')}",
            "emergency": False
        })
    st.rerun()


# ==============================================================================
# MAIN LAYOUT: TWO COLUMNS (Sidebar Left | AI Assistant Right)
# ==============================================================================
col_side, col_main = st.columns([1, 4.3], gap="large")

# ------------------------------------------------------------------------------
# LEFT COLUMN: YOUR WORKSPACE SIDEBAR (AI assistant Active)
# ------------------------------------------------------------------------------
with col_side:
    sidebar_html = (
        '<div class="workspace-sidebar">'
        '<div class="workspace-eyebrow">YOUR WORKSPACE</div>'
        '<a href="/Dashboard" target="_self" class="workspace-item"><span>Dashboard</span></a>'
        '<div class="workspace-divider"></div>'
        '<a href="/AI_Chatbot" target="_self" class="workspace-item active" style="background-color: #dff2f1 !important; color: #076c70 !important;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#076c70" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
        '<span style="color: #076c70 !important; font-weight: 800;">AI assistant</span>'
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
        '</div>'
    )
    st.markdown(sidebar_html, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# RIGHT COLUMN: AI ASSISTANT CHAT INTERFACE
# ------------------------------------------------------------------------------
with col_main:
    # Header Row: Eyebrow + Title on left | Informational only badge on right
    header_html = (
        '<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 10px;">'
        '<div>'
        '<span style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">YOUR AI COMPANION</span>'
        '<h1 style="font-size: 2.15rem; font-weight: 800; color: #193648; margin: 0.25rem 0 0 0; letter-spacing: -0.02em;">Healthcare assistant</h1>'
        '</div>'
        '<span style="background: #eaf6f4; color: #087c76; font-size: 0.8rem; font-weight: 700; padding: 6px 16px; border-radius: 20px;">Informational only · Non-diagnostic</span>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # CHAT PANE: Welcome Card, Stream, Prompt Chips, and Input Bar
    # --------------------------------------------------------------------------
    # Welcome Card (Canva Style)
    welcome_banner = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 18px; padding: 18px 22px; display: flex; align-items: center; gap: 16px; margin-bottom: 1.5rem; box-shadow: 0 4px 18px rgba(24, 75, 103, 0.03);">'
        '<div style="width: 44px; height: 44px; border-radius: 12px; background: #eaf6f4; display: flex; align-items: center; justify-content: center; color: #087c76;">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#087c76" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path>'
        '</svg>'
        '</div>'
        '<div>'
        '<h2 style="font-size: 1.15rem; font-weight: 800; color: #193648; margin: 0 0 2px 0;">Hello! How can I help you today?</h2>'
        '<p style="color: #637d8c; font-size: 0.88rem; margin: 0;">Ask for general health information in everyday language.</p>'
        '</div>'
        '</div>'
    )
    st.markdown(welcome_banner, unsafe_allow_html=True)

    # Message Stream
    for msg in st.session_state["canva_chat_log"]:
        if msg["role"] == "user":
            user_msg_html = (
                '<div style="display: flex; justify-content: flex-end; margin-bottom: 16px;">'
                f'<div style="background: #11556e; color: #FFFFFF; border-radius: 18px 18px 4px 18px; padding: 14px 22px; max-width: 72%; font-size: 0.94rem; font-weight: 500; line-height: 1.5; box-shadow: 0 4px 14px rgba(17, 85, 110, 0.18);">{msg["content"]}</div>'
                '</div>'
            )
            st.markdown(user_msg_html, unsafe_allow_html=True)
        else:
            is_emerg = msg.get("emergency", False) or "CRITICAL MEDICAL EMERGENCY" in msg["content"]
            if is_emerg:
                asst_msg_html = (
                    '<div style="display: flex; justify-content: flex-start; margin-bottom: 16px;">'
                    f'<div style="background: #fff5f5; border: 2px solid #e53e3e; border-radius: 18px 18px 18px 4px; padding: 18px 22px; max-width: 86%; color: #9b2c2c; font-size: 0.94rem; line-height: 1.6; box-shadow: 0 4px 18px rgba(229, 62, 62, 0.12);">{msg["content"]}</div>'
                    '</div>'
                )
            else:
                sources_html = ""
                if msg.get("sources"):
                    src_items = "".join([
                        f'<span style="background: #e2eff3; color: #0a5f70; font-size: 0.76rem; font-weight: 600; padding: 4px 10px; border-radius: 6px; margin-right: 6px; margin-top: 4px; display: inline-block;">📚 {s.get("document_title", "Clinical Care Guideline")}</span>'
                        for s in msg["sources"]
                    ])
                    sources_html = f'<div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #d4e8eb;">{src_items}</div>'

                asst_msg_html = (
                    '<div style="display: flex; justify-content: flex-start; margin-bottom: 16px;">'
                    f'<div style="background: #eef6f6; color: #193648; border-radius: 18px 18px 18px 4px; padding: 16px 22px; max-width: 84%; font-size: 0.94rem; line-height: 1.6; box-shadow: 0 2px 8px rgba(24, 75, 103, 0.02);">{msg["content"]}{sources_html}</div>'
                    '</div>'
                )
            st.markdown(asst_msg_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------------
    # TRY A QUESTION (Canva Prompt Chips Grid)
    # ----------------------------------------------------------------------
    try_q_header = '<div style="color: #637d8c; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px;">TRY A QUESTION</div>'
    st.markdown(try_q_header, unsafe_allow_html=True)

    st.markdown('<div class="prompt-chip-btn">', unsafe_allow_html=True)
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        if st.button("Explain common health conditions.", key="chip_cond", use_container_width=True):
            handle_send_message("Can you explain common health conditions in simple language?")

        if st.button("Learn about preventive healthcare.", key="chip_prev", use_container_width=True):
            handle_send_message("What should I know about everyday preventive healthcare?")

    with q_col2:
        if st.button("Understand medical terminology.", key="chip_term", use_container_width=True):
            handle_send_message("Help me understand medical terminology often found on test results.")

        if st.button("Understand laboratory reports.", key="chip_labs", use_container_width=True):
            handle_send_message("How do reference ranges work on laboratory reports?")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------------
    # CHAT INPUT BAR & SEND ACTION
    # ----------------------------------------------------------------------
    with st.form("assistant_chat_input_form", clear_on_submit=True):
        in_col_clip, in_col_text, in_col_send, in_col_new = st.columns([0.05, 0.69, 0.13, 0.13])
        with in_col_clip:
            st.markdown(
                '<div style="height: 48px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #718a97; cursor: pointer;" title="Attach records (illustrative)">📎</div>',
                unsafe_allow_html=True
            )
        with in_col_text:
            query = st.text_input(
                "Your question",
                placeholder="Ask a general health question...",
                label_visibility="collapsed"
            )
        with in_col_send:
            send_clicked = st.form_submit_button("Send", type="primary", use_container_width=True)
        with in_col_new:
            new_clicked = st.form_submit_button("＋ New", use_container_width=True)

        if new_clicked:
            st.session_state["active_convo_id"] = None
            st.session_state["canva_chat_log"] = [
                {
                    "role": "assistant",
                    "content": f"Hi {first_name}! I can help explain medical terms, symptoms, and laboratory values in clear everyday language. What would you like to explore?"
                }
            ]
            st.rerun()

        if send_clicked and query:
            handle_send_message(query)

    # Muted Informational Disclaimer
    caption_html = '<p style="color: #718a97; font-size: 0.8rem; line-height: 1.5; margin-top: 10px; margin-bottom: 0;">AI responses are educational, informational, and not medical diagnoses. For personal concerns, consult a qualified professional.</p>'
    st.markdown(caption_html, unsafe_allow_html=True)

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
    '<div style="display: flex; direction: column; gap: 8px; font-size: 0.88rem; color: #FFFFFF;">'
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
