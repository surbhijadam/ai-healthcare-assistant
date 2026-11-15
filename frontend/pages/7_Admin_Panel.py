import streamlit as st
import os
import sys

# Ensure frontend root and project root are in path for imports
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
project_root = os.path.abspath(os.path.join(frontend_dir, ".."))
for p in [frontend_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from api_client import api_client
    from components.auth_guard import require_auth
except ImportError:
    from frontend.api_client import api_client
    from frontend.components.auth_guard import require_auth

# Configure page settings
st.set_page_config(
    page_title="Admin Dashboard | MediCare AI",
    page_icon="🛡️",
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
</style>""",
    unsafe_allow_html=True
)

# Enforce Administrator Authorization: Only authenticated users with ROLE_ADMIN can access
user_session = require_auth(page_title="Admin Dashboard", required_role="ROLE_ADMIN")
admin_token = st.session_state.get("token")
is_admin_logged_in = user_session.get("role") == "ROLE_ADMIN"

# Fetch live administrative metrics with Canva fallbacks
stats_res = api_client.get_admin_stats(custom_token=admin_token)
stats_data = stats_res.get("data", {}) if stats_res.get("success") else {}

reg_users = f"{stats_data.get('total_registered_users', 0):,}"
act_users = f"{stats_data.get('active_users', 0):,}"
kb_docs = f"{stats_data.get('knowledge_base_documents', 0):,}"
ai_interactions = f"{stats_data.get('assistant_interactions_30_days', 0):,}"

# ==============================================================================
# TOP NAVBAR (100% Canva Layout: Logo Left | Menu Center | Auth Right)
# ==============================================================================
user_greeting = f'<a href="/Profile" target="_self" class="canva-nav-link" style="color: #087c76; font-weight: 700;">👤 {user_session.get("full_name", "Admin")}</a>'

top_navbar_html = f"""
<div style="background: #FFFFFF; border-bottom: 1px solid #dce9ef; padding: 12px 24px; border-radius: 16px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04);">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span class="iconbox" style="margin: 0; width: 38px; height: 38px; font-size: 1.15rem; background: #e8f6f3; color: #087c76;">🩺</span>
<span style="color: #155c73; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;">MediCare AI</span>
</div>
<div style="display: flex; align-items: center; gap: 16px; font-weight: 700; font-size: 0.92rem;">
<a href="/" target="_self" class="canva-nav-link">Home</a>
<a href="/#features" target="_self" class="canva-nav-link">Features</a>
<a href="/Dashboard" target="_self" class="canva-nav-link">Dashboard</a>
<a href="/About" target="_self" class="canva-nav-link">About</a>
<a href="/Contact" target="_self" class="canva-nav-link">Contact</a>
</div>
<div style="display: flex; align-items: center; gap: 10px;">
{user_greeting}
</div>
</div>
</div>
"""
st.markdown(top_navbar_html, unsafe_allow_html=True)

# ==============================================================================
# MAIN LAYOUT: TWO COLUMNS (Sidebar Left | Admin Dashboard Right)
# ==============================================================================
col_side, col_main = st.columns([1, 4.3], gap="large")

# ------------------------------------------------------------------------------
# LEFT COLUMN: WORKSPACE SIDEBAR (ADMIN PREVIEW Active)
# ------------------------------------------------------------------------------
with col_side:
    sidebar_html = (
        '<div class="workspace-sidebar">'
        '<div class="workspace-eyebrow">ADMIN PREVIEW</div>'
        '<a href="/Admin_Panel" target="_self" class="workspace-item active" style="background-color: #dff2f1 !important; color: #076c70 !important;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#076c70" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
        '<span style="color: #076c70 !important; font-weight: 800;">Admin preview</span>'
        '</a>'
        '<div style="margin-top: 14px;"></div>'
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
        '<a href="/Profile" target="_self" class="workspace-item">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
        '<span>Profile</span>'
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
# RIGHT COLUMN: ADMIN DASHBOARD
# ------------------------------------------------------------------------------
with col_main:
    # Header Section
    header_html = (
        '<div style="margin-bottom: 1.2rem;">'
        '<span style="color: #087c76; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;">PLATFORM OVERVIEW</span>'
        '<h1 style="font-size: 2.15rem; font-weight: 800; color: #193648; margin: 0.25rem 0 0.8rem 0; letter-spacing: -0.02em;">Admin dashboard</h1>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # Demo Notice / Live Telemetry Banner
    banner_text = (
        "Live administrative session connected · Real-time telemetry, RBAC enforcement, and audit logs active."
        if is_admin_logged_in else
        "Administrative preview mode · Connected to live backend metrics and clinical governance telemetry."
    )
    demo_banner_html = (
        '<div style="background: #fff8e9; border: 1px solid #fae6be; color: #74531a; border-radius: 12px; padding: 13px 20px; font-size: 0.88rem; font-weight: 500; line-height: 1.5; margin-bottom: 2rem;">'
        f'{banner_text}'
        '</div>'
    )
    st.markdown(demo_banner_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 1: 4 CANVA STATISTICS CARDS (Dynamically populated)
    # --------------------------------------------------------------------------
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4, gap="medium")

    with stat_col1:
        st.markdown(
            f'<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 22px 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); min-height: 110px;">'
            f'<div style="color: #637d8c; font-size: 0.88rem; font-weight: 600;">Total registered users</div>'
            f'<div style="font-size: 2.2rem; font-weight: 800; color: #193648; line-height: 1.1; margin-top: 8px;">{reg_users}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with stat_col2:
        st.markdown(
            f'<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 22px 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); min-height: 110px;">'
            f'<div style="color: #637d8c; font-size: 0.88rem; font-weight: 600;">Active users</div>'
            f'<div style="font-size: 2.2rem; font-weight: 800; color: #193648; line-height: 1.1; margin-top: 8px;">{act_users}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with stat_col3:
        st.markdown(
            f'<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 22px 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); min-height: 110px;">'
            f'<div style="color: #637d8c; font-size: 0.88rem; font-weight: 600;">Knowledge base documents</div>'
            f'<div style="font-size: 2.2rem; font-weight: 800; color: #193648; line-height: 1.1; margin-top: 8px;">{kb_docs}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with stat_col4:
        st.markdown(
            f'<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 22px 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); min-height: 110px;">'
            f'<div style="color: #637d8c; font-size: 0.88rem; font-weight: 600;">Assistant interactions · 30 days</div>'
            f'<div style="font-size: 2.2rem; font-weight: 800; color: #193648; line-height: 1.1; margin-top: 8px;">{ai_interactions}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 2: SYSTEM USAGE BAR CHART (LEFT) & RECENT ACTIVITY (RIGHT)
    # --------------------------------------------------------------------------
    col_chart, col_act = st.columns([1.4, 1], gap="medium")

    with col_chart:
        chart_html = (
            '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); height: 100%;">'
            '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">'
            '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0;">System usage · weekly distribution</h2>'
            '<span style="background: #eaf6f4; color: #087c76; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 20px;">Live Telemetry</span>'
            '</div>'
            '<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 200px; color: #718a97; font-size: 0.9rem; text-align: center; border: 1px dashed #dce9ef; border-radius: 14px; padding: 20px;">'
            '<div style="font-size: 1.8rem; margin-bottom: 8px;">📊</div>'
            '<div style="font-weight: 700; color: #193648; margin-bottom: 4px;">Usage telemetry active</div>'
            '<div>Weekly distribution will aggregate dynamically as platform interactions occur.</div>'
            '</div>'
            '</div>'
        )
        st.markdown(chart_html, unsafe_allow_html=True)

    with col_act:
        act_res = api_client.get_admin_activity(custom_token=admin_token)
        act_items = act_res.get("data", []) if act_res.get("success") else []
        if act_items:
            activity_rows_html = "".join([
                (
                    '<div>'
                    '<div style="display: flex; align-items: center; gap: 8px;">'
                    '<span style="font-size: 1.15rem; color: #193648; line-height: 1;">•</span>'
                    f'<strong style="color: #193648; font-size: 0.95rem; font-weight: 700;">{item.get("title", "Activity")}</strong>'
                    '</div>'
                    f'<div style="color: #718a97; font-size: 0.85rem; margin-left: 18px; margin-top: 2px;">{item.get("timestamp_desc", "Recently")}</div>'
                    '</div>'
                )
                for item in act_items[:4]
            ])
            body_act = f'<div style="display: flex; flex-direction: column; gap: 18px;">{activity_rows_html}</div>'
        else:
            body_act = '<div style="color: #718a97; font-size: 0.9rem; padding: 24px 0; text-align: center;">No recent system activity recorded.</div>'

        act_html = (
            '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); height: 100%;">'
            '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 20px 0;">Recent system activity</h2>'
            f'{body_act}'
            '</div>'
        )
        st.markdown(act_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 3: USER MANAGEMENT TABLE
    # --------------------------------------------------------------------------
    users_res = api_client.get_admin_users(custom_token=admin_token)
    user_rows = users_res.get("data", []) if users_res.get("success") else []
    if user_rows:
        table_rows_html = "".join([
            (
                '<tr style="border-bottom: 1px solid #edf4f7;">'
                f'<td style="padding: 14px; font-weight: 700; color: #193648;">{u.get("name", "User")}</td>'
                f'<td style="padding: 14px; color: #637d8c;">{u.get("role", "Member")}</td>'
                f'<td style="padding: 14px;"><span style="background: {"#eaf6f4" if u.get("status") == "Active" else "#e8f2f8"}; color: {"#087c76" if u.get("status") == "Active" else "#1a6c8e"}; padding: 4px 14px; border-radius: 12px; font-weight: 700; font-size: 0.82rem; display: inline-block;">{u.get("status", "Active")}</span></td>'
                f'<td style="padding: 14px; color: #637d8c;">{u.get("last_active", "—")}</td>'
                '</tr>'
            )
            for u in user_rows
        ])
        tbody_users = f'<tbody>{table_rows_html}</tbody>'
    else:
        tbody_users = '<tbody><tr><td colspan="4" style="padding: 24px; text-align: center; color: #718a97; font-size: 0.9rem;">No registered user accounts found.</td></tr></tbody>'

    users_table_html = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); margin-top: 1.8rem; overflow-x: auto;">'
        '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 16px 0;">User management accounts</h2>'
        '<table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">'
        '<thead>'
        '<tr style="border-bottom: 1px solid #e5edf0; color: #637d8c; font-size: 0.88rem; font-weight: 600;">'
        '<th style="padding: 12px 14px; font-weight: 600;">Name</th>'
        '<th style="padding: 12px 14px; font-weight: 600;">Role</th>'
        '<th style="padding: 12px 14px; font-weight: 600;">Status</th>'
        '<th style="padding: 12px 14px; font-weight: 600;">Last active</th>'
        '</tr>'
        '</thead>'
        f'{tbody_users}'
        '</table>'
        '</div>'
    )
    st.markdown(users_table_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ROW 4: HEALTHCARE KNOWLEDGE DOCUMENTS & INGESTION FORM (FR-04.1 / FR-08.1)
    # --------------------------------------------------------------------------
    docs_res = api_client.get_admin_knowledge_documents(custom_token=admin_token)
    doc_items = docs_res.get("data", []) if docs_res.get("success") else []
    if doc_items:
        doc_cards_html = "".join([
            (
                '<div style="background: #eef8f8; border-radius: 14px; padding: 18px 22px;">'
                f'<div style="font-size: 0.95rem; font-weight: 700; color: #193648; margin-bottom: 12px;">{d.get("title", "Guideline")}</div>'
                f'<span style="background: #eaf6f4; color: #087c76; padding: 4px 14px; border-radius: 12px; font-weight: 700; font-size: 0.82rem; display: inline-block;">{d.get("status", "Reviewed")}</span>'
                '</div>'
            )
            for d in doc_items
        ])
        content_docs = f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">{doc_cards_html}</div>'
    else:
        content_docs = '<div style="color: #718a97; font-size: 0.9rem; padding: 24px; text-align: center; border: 1px dashed #dce9ef; border-radius: 14px;">No knowledge base documents ingested yet. Use the form below to ingest clinical care guidelines.</div>'

    docs_html = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); margin-top: 1.8rem;">'
        '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 18px 0;">Healthcare knowledge documents</h2>'
        f'{content_docs}'
        '</div>'
    )
    st.markdown(docs_html, unsafe_allow_html=True)

    # Interactive Guideline Ingestion Form (FR-04.1)
    with st.expander("➕ Ingest Clinical Guideline into Knowledge Base (FR-04.1 / FR-08.1)"):
        with st.form("admin_ingest_guideline_form"):
            g_title = st.text_input("Guideline Title", placeholder="e.g. ADA 2026 Type 2 Diabetes Management")
            g_cat = st.selectbox("Category", ["Clinical Guideline", "Laboratory Medicine", "Cardiology", "Preventive Care", "Pharmacotherapy"])
            g_url = st.text_input("Source URL (optional)", placeholder="https://diabetes.org/guidelines/2026")
            g_content = st.text_area("Guideline Content / Clinical Text", placeholder="Paste clinical guidance, thresholds, diagnostic criteria...", height=120)
            submitted = st.form_submit_button("Ingest & Vectorize Document", use_container_width=True)
            if submitted:
                if not g_title.strip() or not g_content.strip():
                    st.error("Title and Content are required.")
                else:
                    with st.spinner("Chunking and generating 384-dim vector embeddings..."):
                        res = api_client.create_knowledge_document(
                            title=g_title.strip(),
                            category=g_cat,
                            content=g_content.strip(),
                            source_url=g_url.strip(),
                            custom_token=admin_token
                        )
                        if res.get("success"):
                            st.success(f"Guideline '{g_title}' successfully ingested into RAG repository!")
                            st.rerun()
                        else:
                            st.error(f"Failed to ingest guideline: {res.get('message', 'Unknown error')}")

    # --------------------------------------------------------------------------
    # ROW 5: AUDIT LOGS TELEMETRY (FR-08.2)
    # --------------------------------------------------------------------------
    logs_res = api_client.get_admin_audit_logs(custom_token=admin_token)
    audit_rows = logs_res.get("data", []) if logs_res.get("success") else []
    if audit_rows:
        audit_table_rows_html = "".join([
            (
                '<tr style="border-bottom: 1px solid #edf4f7;">'
                f'<td style="padding: 10px 14px; font-weight: 600; color: #193648;">{str(l.get("timestamp", "—"))[:19].replace("T", " ")}</td>'
                f'<td style="padding: 10px 14px; font-weight: 700; color: #155c73;">{l.get("action", "EVENT")}</td>'
                f'<td style="padding: 10px 14px;"><span style="background: {"#eaf6f4" if l.get("status") == "SUCCESS" else "#fde8e8"}; color: {"#087c76" if l.get("status") == "SUCCESS" else "#c53030"}; padding: 3px 10px; border-radius: 8px; font-weight: 700; font-size: 0.78rem;">{l.get("status", "SUCCESS")}</span></td>'
                f'<td style="padding: 10px 14px; color: #637d8c;">{l.get("user_id") if l.get("user_id") is not None else "—"}</td>'
                f'<td style="padding: 10px 14px; color: #718a97; font-family: monospace;">{l.get("ip_address", "127.0.0.1")}</td>'
                '</tr>'
            )
            for l in audit_rows[:10]
        ])
        audit_tbody = f'<tbody>{audit_table_rows_html}</tbody>'
    else:
        audit_tbody = '<tbody><tr><td colspan="5" style="padding: 24px; text-align: center; color: #718a97; font-size: 0.9rem;">No clinical governance audit logs recorded yet.</td></tr></tbody>'

    audit_section_html = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); margin-top: 1.8rem; overflow-x: auto;">'
        '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 16px 0;">Clinical governance audit logs (FR-08.2)</h2>'
        '<table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.86rem;">'
        '<thead>'
        '<tr style="border-bottom: 1px solid #e5edf0; color: #637d8c; font-size: 0.82rem; font-weight: 600;">'
        '<th style="padding: 10px 14px;">Timestamp (UTC)</th>'
        '<th style="padding: 10px 14px;">Action</th>'
        '<th style="padding: 10px 14px;">Status</th>'
        '<th style="padding: 10px 14px;">User ID</th>'
        '<th style="padding: 10px 14px;">IP Address</th>'
        '</tr>'
        '</thead>'
        f'{audit_tbody}'
        '</table>'
        '</div>'
    )
    st.markdown(audit_section_html, unsafe_allow_html=True)

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
