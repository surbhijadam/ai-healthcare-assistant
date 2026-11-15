import streamlit as st

def render_top_header():
    """Renders the Canva-aligned top header bar with branding and user status."""
    is_auth = st.session_state.get("authenticated", False)
    user = st.session_state.get("user") or {}
    
    col_brand, col_nav, col_user = st.columns([3, 4, 3])
    
    with col_brand:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0; margin-top: 6px;">
                <span class="iconbox" style="margin: 0; width: 38px; height: 38px; font-size: 1.15rem;">🩺</span>
                <span style="color: #155c73; font-size: 1.3rem; font-weight: 800; letter-spacing: -0.02em;">
                    MediCare AI
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_nav:
        st.markdown(
            """
            <div style="padding-top: 18px;">
                <span class="tiny muted">Personal overview · 14 November 2026</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_user:
        st.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)
        if is_auth:
            c_name, c_btn = st.columns([2, 1])
            with c_name:
                initials = "".join([part[0] for part in user.get("full_name", "User").split()[:2]]).upper() or "AS"
                role = user.get("role", "user").upper()
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px;">
                        <span style="font-size: 0.8rem; font-weight: 700; color: #155c73;">{user.get('full_name', 'User')}</span>
                        <span class="badge badge-blue">{role}</span>
                        <div style="width: 34px; height: 34px; border-radius: 50%; background: #d5eee9; color: #08675f; display: grid; place-items: center; font-weight: 800; font-size: 0.85rem;">
                            {initials}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c_btn:
                if st.button("🚪 Logout", key="top_logout_btn", use_container_width=True):
                    st.session_state["authenticated"] = False
                    st.session_state["token"] = None
                    st.session_state["user"] = None
                    st.rerun()
        else:
            st.markdown(
                """
                <div style="display: flex; justify-content: flex-end; align-items: center; gap: 6px;">
                    <a href="/Login_Register?mode=login" target="_self" style="color: #087c76; font-size: 0.85rem; font-weight: 700; text-decoration: none;">Login / Register</a>
                </div>
                """,
                unsafe_allow_html=True
            )
