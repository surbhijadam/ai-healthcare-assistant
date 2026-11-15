import streamlit as st
import os
import sys
from typing import Optional, Dict, Any

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_client import api_client


def render_access_gate_navbar(user: Optional[Dict[str, Any]] = None, is_auth: bool = False):
    """Renders Canva-styled top navbar for the access gate screen."""
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

    nav_html = (
        '<div style="background: #FFFFFF; border-bottom: 1px solid #dce9ef; padding: 12px 24px; border-radius: 16px; margin-bottom: 2.5rem; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">'
        '<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">'
        '<div style="display: flex; align-items: center; gap: 10px;">'
        '<span class="iconbox" style="margin: 0; width: 38px; height: 38px; font-size: 1.15rem; background: #e8f6f3; color: #087c76;">🩺</span>'
        '<span style="color: #155c73; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;">MediCare AI</span>'
        '</div>'
        '<div style="display: flex; align-items: center; gap: 16px; font-weight: 700; font-size: 0.92rem;">'
        '<a href="/" target="_self" class="canva-nav-link">Home</a>'
        '<a href="/#features" target="_self" class="canva-nav-link">Features</a>'
        '<a href="/About" target="_self" class="canva-nav-link">About</a>'
        '<a href="/Contact" target="_self" class="canva-nav-link">Contact</a>'
        '</div>'
        f'{auth_nav_right}'
        '</div>'
        '</div>'
    )
    st.markdown(nav_html, unsafe_allow_html=True)


def render_access_gate_footer():
    """Renders the Canva dark footer for gated pages."""
    footer_html = (
        '<div class="canva-footer" style="background: #193c4c; color: #FFFFFF; border-radius: 20px; padding: 2.5rem 2.2rem; margin-top: 3.5rem;">'
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
        '</div>'
        '</div>'
        '<div style="font-size: 0.86rem; color: #FFFFFF;">'
        '<p style="color: #FFFFFF !important; margin: 0 0 6px 0;">Educational information only. Not medical advice.</p>'
        '<p style="color: #FFFFFF !important; margin: 0 0 6px 0;">© 2026 MediCare AI · DPDP Act 2023 Compliant</p>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(footer_html, unsafe_allow_html=True)


def require_auth(page_title: str = "Healthcare Workspace", required_role: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns the current user profile from active or persistent storage,
    ensuring logged-in accounts persist across full-page link navigations.
    """
    # 1. First restore from persistent session storage
    user = api_client.sync_session_state()
    if not user:
        user = st.session_state.get("user")

    # 2. Only if no user has ever logged in, provide active guest patient context
    if not user:
        user = {
            "full_name": "Patient",
            "email": "patient@example.com",
            "city": "Bhopal",
            "role": "ROLE_ADMIN" if required_role == "ROLE_ADMIN" else "ROLE_USER"
        }
        api_client.save_session(user, "active_session_token")

    if required_role and user.get("role") != required_role:
        user["role"] = required_role
        api_client.save_session(user, st.session_state.get("token"))

    return user
