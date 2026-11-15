import streamlit as st

def render_medical_disclaimer():
    """Renders the standard mandatory Canva healthcare safety disclaimer."""
    st.markdown(
        """
        <div class="medical-disclaimer-box">
            <span>
                <strong>Healthcare safety notice:</strong>
                This experience offers general educational information only.
                It cannot diagnose, prescribe, or replace advice from a qualified healthcare professional.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_emergency_banner(trigger_reason: str = None):
    """Renders high-visibility emergency alert when acute symptoms are suspected."""
    reason_text = f"Trigger detected: <em>{trigger_reason}</em>. " if trigger_reason else ""
    st.markdown(
        f"""
        <div class="emergency-alert-box">
            <h4>🚨 Urgent Medical Attention Required</h4>
            <p style="margin-bottom: 6px; font-size: 0.92rem;">
                {reason_text}If you or someone near you is experiencing severe chest pain, sudden numbness, difficulty speaking, severe shortness of breath, or uncontrolled bleeding:
            </p>
            <p style="font-weight: 700; margin-bottom: 0; font-size: 0.95rem;">
                👉 Call Emergency Services (<strong>112</strong> in India / <strong>911</strong> in US) or proceed to the nearest hospital Emergency Department immediately.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_demo_notice(custom_text: str = None):
    """Renders the educational notice note."""
    text = custom_text or "Notice: Health information provided is for educational purposes. Always consult a qualified clinician."
    st.markdown(
        f"""
        <div class="demo-box">
            <span>ℹ️</span>
            <span>{text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_footer():
    """Renders the Canva dark footer with navigation and legal disclaimers."""
    st.markdown(
        """
        <div class="canva-footer">
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
                <div style="max-width: 380px;">
                    <strong style="font-size: 1.2rem; display: flex; align-items: center; gap: 8px; color: #FFFFFF;">
                        ✚ MediCare AI
                    </strong>
                    <p style="color: #FFFFFF !important; font-size: 0.86rem; margin-top: 8px; line-height: 1.6;">
                        A more human way to explore everyday health information and keep records organized.
                    </p>
                </div>
                <div style="font-size: 0.86rem; color: #FFFFFF;">
                    <p style="color: #FFFFFF !important; margin: 0 0 6px 0;"><strong>Support:</strong> hello@medicareai.example</p>
                    <p style="color: #FFFFFF !important; margin: 0 0 6px 0;">Educational information only. Not medical advice.</p>
                    <p style="color: #FFFFFF !important; font-size: 0.78rem; margin-top: 12px;">© 2026 MediCare AI · All rights reserved</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
