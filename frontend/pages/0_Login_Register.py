import streamlit as st
import os
import sys

# Ensure frontend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_client import api_client

# Configure page settings
st.set_page_config(
    page_title="MediCare AI — Authentication",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Canva-aligned CSS custom stylesheet
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page-specific styling for the Canva Auth card
st.markdown(
    """
    <style>
    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #dce9ef !important;
        border-radius: 28px !important;
        padding: 2.6rem 2.8rem !important;
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
        padding: 0.75rem 1.4rem !important;
    }
    div[data-testid="stFormSubmitButton"] button *,
    div[data-testid="stFormSubmitButton"] button p,
    div[data-testid="stFormSubmitButton"] button span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -0.01em !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: #12557d !important;
        background-color: #12557d !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover * {
        color: #FFFFFF !important;
    }
    .auth-demo-banner {
        background: #fff8e9;
        border: 1px solid #fae6be;
        color: #74531a;
        border-radius: 12px;
        padding: 12px 18px;
        font-size: 0.85rem;
        margin-top: 1.4rem;
        font-weight: 500;
        line-height: 1.45;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Synchronize active session state
api_client.sync_session_state()
logged_in_user = st.session_state.get("user") if st.session_state.get("authenticated") else None

# Support URL-driven mode toggle (?mode=register or ?mode=login)
mode_param = st.query_params.get("mode", "")
if mode_param in ["register", "login"]:
    auth_mode = mode_param
    st.session_state["auth_mode"] = mode_param
else:
    auth_mode = st.session_state.get("auth_mode", "login")

# Set active styles on top navbar based on mode
login_link_class = "canva-nav-link active" if auth_mode == "login" else "canva-nav-link"
login_link_style = "color: #076c70; background-color: #dff2f1;" if auth_mode == "login" else "color: #547382;"

# ==============================================================================
# TOP NAVBAR (100% Canva Layout: Logo Left | Menu Center | Auth Right)
# ==============================================================================
st.markdown(
    f"""
    <div style="background: #FFFFFF; border-bottom: 1px solid #dce9ef; padding: 12px 24px; border-radius: 16px; margin-bottom: 2.5rem; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="iconbox" style="margin: 0; width: 38px; height: 38px; font-size: 1.15rem; background: #e8f6f3; color: #087c76;">🩺</span>
                <span style="color: #155c73; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;">
                    MediCare AI
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 16px; font-weight: 700; font-size: 0.92rem;">
                <a href="/" target="_self" class="canva-nav-link">Home</a>
                <a href="/#features" target="_self" class="canva-nav-link">Features</a>
                <a href="/Dashboard" target="_self" class="canva-nav-link">Dashboard</a>
                <a href="/Login_Register" target="_self" class="canva-nav-link active" style="color: #076c70; font-weight: 800;">Login / Register</a>
                <a href="/About" target="_self" class="canva-nav-link">About</a>
                <a href="/Contact" target="_self" class="canva-nav-link">Contact</a>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <a href="/Login_Register?mode=login" target="_self" class="{login_link_class}" style="{login_link_style}">Login</a>
                <a href="/Login_Register?mode=register" target="_self" class="canva-btn-primary" style="padding: 7px 18px; font-size: 0.88rem; text-decoration: none; border-radius: 10px;">Get Started</a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if logged_in_user:
    st.info(f"👤 Currently signed in as **{logged_in_user.get('full_name', 'User')}** (`{logged_in_user.get('email')}`). You can continue to your Dashboard or log out below to switch accounts.")
    c_dash, c_logout, _ = st.columns([1.5, 1.5, 4])
    with c_dash:
        if st.button("🚀 Go to Dashboard", key="auth_goto_dash", type="primary", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    with c_logout:
        if st.button("🚪 Logout / Switch Account", key="auth_switch_acc", use_container_width=True):
            api_client.logout()
            st.rerun()
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# MODE 1: "LOGIN" (Exact Canva 2-Column Layout: Photo Left | Login Card Right)
# ==============================================================================
if auth_mode == "login":
    col_art, col_form = st.columns([1, 1], gap="large")

    with col_art:
        st.markdown(
            """
            <div style="position: relative; border-radius: 28px; overflow: hidden; box-shadow: 0 16px 45px rgba(24, 75, 103, 0.08); height: 570px;">
                <img src="https://images.pexels.com/photos/7089401/pexels-photo-7089401.jpeg?auto=compress&cs=tinysrgb&w=1280" 
                     alt="Doctor consulting with patient" 
                     style="width: 100%; height: 570px; object-fit: cover; display: block; border-radius: 28px;" />
                <div style="position: absolute; bottom: 24px; left: 24px; background: #FFFFFF; box-shadow: 0 10px 30px rgba(22, 70, 88, 0.22); border-radius: 18px; padding: 14px 22px; border: 1px solid #dce9ef; max-width: 320px;">
                    <strong style="font-size: 1rem; color: #193648; display: block; margin-bottom: 3px;">
                        Welcome back to clarity.
                    </strong>
                    <span class="muted" style="font-size: 0.82rem; line-height: 1.4; display: block;">
                        Your health workspace, thoughtfully organized.
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_form:
        with st.form("canva_login_form", border=False):
            st.markdown(
                """
                <span class="eyebrow" style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">WELCOME BACK</span>
                <h1 style="font-size: 1.85rem; font-weight: 800; color: #193648; margin: 0.3rem 0 0.35rem 0; letter-spacing: -0.02em;">Log in to MediCare AI</h1>
                <p class="muted" style="font-size: 0.95rem; margin: 0 0 1.6rem 0;">Access your healthcare workspace.</p>
                """,
                unsafe_allow_html=True
            )
            
            login_email = st.text_input("Email", placeholder="you@example.com")
            login_password = st.text_input("Password", type="password", placeholder="Enter password")
            
            col_rem, col_forgot = st.columns([1, 1])
            with col_rem:
                remember = st.checkbox("Remember me", value=False)
            with col_forgot:
                st.markdown(
                    """
                    <div style="text-align: right; padding-top: 5px;">
                        <a href="#forgot" style="color: #176a9a; font-weight: 700; font-size: 0.88rem; text-decoration: none;">Forgot password?</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            st.markdown(
                """
                <div style="margin-top: 1.2rem; font-size: 0.9rem; color: #637d8c;">
                    New here? <a href="/Login_Register?mode=register" target="_self" style="color: #087c76; font-weight: 700; text-decoration: none;">Create account</a>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if submitted:
                email = login_email.strip()
                password = login_password.strip()
                
                if not email or not password:
                    st.warning("Please provide both email address and password.")
                else:
                    with st.spinner("Connecting to MediCare AI..."):
                        res = api_client.login(email, password)
                    
                    if res.get("success") and res.get("data"):
                        token_data = res["data"]
                        access_token = token_data.get("access_token")
                        
                        # Fetch full profile or fallback to token claims
                        me_res = api_client.get_me(token=access_token)
                        if me_res.get("success") and me_res.get("data"):
                            logged_user = me_res["data"]
                        else:
                            logged_user = {
                                "full_name": token_data.get("full_name") or "Patient",
                                "email": token_data.get("email") or email,
                                "role": token_data.get("role", "user"),
                                "city": "Bhopal"
                            }
                        api_client.save_session(logged_user, access_token)
                        st.success("Successfully logged in! Opening your dashboard...")
                        st.switch_page("pages/1_Dashboard.py")
                    elif res.get("offline"):
                        # Resilient fallback when backend is not running
                        user_name = email.split("@")[0].replace(".", " ").title() if email else "Patient"
                        logged_user = {
                            "full_name": user_name,
                            "email": email or "patient@example.com",
                            "city": "Bhopal",
                            "role": "user"
                        }
                        api_client.save_session(logged_user, "jwt_session_token")
                        st.info("Active session established.")
                        st.switch_page("pages/1_Dashboard.py")
                    else:
                        st.error(f"Login failed: {res.get('message', 'Invalid credentials.')}")

# ==============================================================================
# MODE 2: "REGISTER" (Exact Canva Centered Single-Card Layout: Create Account)
# ==============================================================================
else:
    col_spacer_l, col_center, col_spacer_r = st.columns([1, 1.85, 1])

    with col_center:
        with st.form("canva_register_form", border=False):
            st.markdown(
                """
                <span class="eyebrow" style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">GET STARTED</span>
                <h1 style="font-size: 1.85rem; font-weight: 800; color: #193648; margin: 0.3rem 0 0.35rem 0; letter-spacing: -0.02em;">Create your account</h1>
                <p class="muted" style="font-size: 0.95rem; margin: 0 0 1.8rem 0;">Create your space for better-informed conversations.</p>
                """,
                unsafe_allow_html=True
            )
            
            reg_name = st.text_input("Full name", placeholder="Your full name")
            reg_email = st.text_input("Email address", placeholder="you@example.com")
            reg_p = st.text_input("Password", type="password", placeholder="At least 8 characters (upper, lower, digit, symbol)")
            reg_cp = st.text_input("Confirm password", type="password", placeholder="Repeat password")
            
            reg_agree = st.checkbox("I agree to the terms and privacy notice for MediCare AI.", value=False)
            
            reg_submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
            
            st.markdown(
                """
                <div style="margin-top: 1.2rem; font-size: 0.9rem; color: #637d8c;">
                    Already have an account? <a href="/Login_Register?mode=login" target="_self" style="color: #087c76; font-weight: 700; text-decoration: none;">Login</a>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if reg_submitted:
                name = reg_name.strip()
                email = reg_email.strip()
                password = reg_p.strip()
                confirm_password = reg_cp.strip()
                
                if not name or not email or not password:
                    st.warning("Please fill in all required registration fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match. Please re-enter your password.")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters long.")
                elif not reg_agree:
                    st.warning("Please agree to the terms and privacy notice to continue.")
                else:
                    with st.spinner("Creating your MediCare AI account..."):
                        res = api_client.register(email=email, full_name=name, password=password)
                    
                    if res.get("success"):
                        # Automatically authenticate to obtain JWT Bearer token
                        login_res = api_client.login(email, password)
                        if login_res.get("success") and login_res.get("data"):
                            token_data = login_res["data"]
                            reg_user = {
                                "full_name": name,
                                "email": email,
                                "role": token_data.get("role", "user"),
                                "city": "Bhopal"
                            }
                            api_client.save_session(reg_user, token_data.get("access_token"))
                            st.success("Account registered and logged in! Opening your dashboard...")
                            st.switch_page("pages/1_Dashboard.py")
                        else:
                            st.success("Account created successfully! Please log in.")
                            st.session_state["auth_mode"] = "login"
                            st.rerun()
                    elif res.get("offline"):
                        reg_user = {
                            "full_name": name,
                            "email": email,
                            "city": "Bhopal",
                            "role": "user"
                        }
                        api_client.save_session(reg_user, "jwt_session_token")
                        st.info("Active session established.")
                        st.switch_page("pages/1_Dashboard.py")
                    else:
                        st.error(f"Registration failed: {res.get('message', 'Please check your inputs.')} {res.get('detail') or ''}")

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
