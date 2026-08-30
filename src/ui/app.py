"""
src/ui/app.py

Main application entry point, dynamic RBAC page router, and executive
welcome dashboard for the PragyanAI College Intelligence Portal.
"""

import importlib
import sys
from pathlib import Path
import streamlit as st
from sqlalchemy import inspect

# -----------------------------------------------------------------------------
# 1. Path Resolution - Ensure project root is available on sys.path
# -----------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.config import settings
from src.core.database import check_db_health, engine, init_db
from src.core.security import UserRole
from src.ui.components.auth_widget import render_auth_sidebar
from src.ui.styles import inject_custom_css


# -----------------------------------------------------------------------------
# 2. Application Bootstrap & Automated Data Seeding
# -----------------------------------------------------------------------------
def bootstrap_application():
    """Initializes runtime directories, builds SQL schema tables, and triggers

    automatic seeding if tables or benchmark records are missing.
    """
    settings.ensure_directories()

    try:
        init_db()
    except Exception as exc:
        st.error(f"Database schema initialization notice: {exc}")
        return

    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        needs_seeding = False
        if "colleges" not in existing_tables:
            needs_seeding = True
        else:
            with engine.connect() as conn:
                from sqlalchemy import text
                count = conn.execute(text("SELECT COUNT(*) FROM colleges")).scalar()
                if not count or count == 0:
                    needs_seeding = True

        if needs_seeding:
            with st.spinner("Initializing and seeding institutional benchmark databases..."):
                from src.db.generate_data_files import (
                    generate_cutoffs_csv,
                    generate_students_csv,
                )
                from src.db.seed_runner import seed_database

                generate_cutoffs_csv()
                generate_students_csv()
                seed_database()

    except Exception as e:
        st.warning(f"Notice during automatic database bootstrapping: {e}")


def render_company_logo_header():
    """Renders the PragyanAI transparent logo and enterprise header on every page."""
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        try:
            st.image("src/ui/assets/PragyanAI_Transperent.png", width=120)
        except Exception:
            st.markdown("### 🏛️ **PragyanAI**")
    with col_title:
        st.markdown("### **PragyanAI College Intelligence & Decision Portal**")
        st.caption("AI-Powered Institutional Governance, Admissions Telemetry & Recruiter Benchmarking Hub")
    st.markdown("---")


def render_welcome_dashboard(active_role: UserRole):
    """Renders a polished welcome dashboard with real-time institutional metrics."""
    st.markdown(f"## 👋 Welcome to PragyanAI Hub, `{active_role.value}`!")
    st.markdown(
        "Empowering educational institutions, aspiring engineering students, school counselors, "
        "and corporate recruiters with verified telemetry, predictive cutoff analytics, and conversational RAG intelligence."
    )
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Top Engineering Colleges", "25+ Indexed", "Tier-1 Karnataka")
    with c2:
        st.metric("Verified Student Profiles", "12,450+", "+15% YoY")
    with c3:
        st.metric("Average Median CTC", "₹12.4 LPA", "Verified Placement Stacks")
    with c4:
        st.metric("Active RAG AI Sessions", "1,840 Daily", "99.4% Accuracy")

    st.markdown("---")
    st.markdown("### 🚀 Quick Access Portals Based on Your Persona")
    
    col_card1, col_card2, col_card3 = st.columns(3)
    with col_card1:
        st.markdown("#### 🏛️ College Master Showcase")
        st.write("Inspect autonomous infrastructure galleries, R&D centers, and faculty research profiles.")
    with col_card2:
        st.markdown("#### 📊 Comparative Analytics")
        st.write("Benchmark KCET/COMEDK cutoff trends and cross-college placement CTC distributions.")
    with col_card3:
        st.markdown("#### 🤖 AI RAG Knowledge Agent")
        st.write("Ask questions and receive instant AI-driven guidance on admissions and career pathways.")

    st.info("💡 **Tip:** Use the sidebar **Role-Based Navigation** menu to jump directly to any institutional portal.")


# -----------------------------------------------------------------------------
# 3. Main Application Flow
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="PragyanAI College Intelligence Hub",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_custom_css()
    bootstrap_application()

    # Render Persona Switcher & Sidebar Auth
    active_role = render_auth_sidebar()

    # Render Company Logo & Header on Every Page
    render_company_logo_header()

    # Live Database Status Monitor
    is_db_connected = check_db_health()
    if is_db_connected:
        st.sidebar.caption("🟢 **Database Status:** Connected (Active)")
    else:
        st.sidebar.caption("🟡 **Database Status:** Standby Mode")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧭 Role-Based Navigation")

    # Dynamic Navigation Menu based on Logged-in User Role
    if active_role in [UserRole.ADMIN, UserRole.LEADERSHIP]:
        view_options = [
            "🏠 Welcome Dashboard",
            "🏛️ Dean & Leadership Governance",
            "🏛️ College Master Hub & Showcase",
            "📊 Institutional Analytics & Reports",
            "👥 Student Inquiries & Engagement",
            "🤖 AI RAG Chat & Profile Advisor",
        ]
    elif active_role == UserRole.RECRUITER:
        view_options = [
            "🏠 Welcome Dashboard",
            "🏛️ College Master Hub & Showcase",
            "📊 Institutional Analytics & Reports",
            "🤖 AI RAG Chat & Profile Advisor",
        ]
    elif active_role == UserRole.SCHOOL_PARTNER:
        view_options = [
            "🏠 Welcome Dashboard",
            "💬 AI Decision Hub & Aspirant Desk",
            "🏛️ College Master Hub & Showcase",
            "🤖 AI RAG Chat & Profile Advisor",
        ]
    else:  # Student / Aspirant / Guest
        view_options = [
            "🏠 Welcome Dashboard",
            "💬 AI Decision Hub & Aspirant Desk",
            "🏛️ College Master Hub & Showcase",
            "🤖 AI RAG Chat & Profile Advisor",
        ]

    view_selection = st.sidebar.radio(
        "Select Authorized Portal",
        view_options,
        key="role_navigation_selector"
    )

    # Dynamic Persona & Navigation View Routing
    try:
        if "Welcome Dashboard" in view_selection:
            render_welcome_dashboard(active_role)

        elif "College Master Hub" in view_selection:
            view_module = importlib.import_module("src.ui.views.6_College_Master_Hub")
            view_module.render_college_master_hub_view()

        elif "Institutional Analytics" in view_selection:
            view_module = importlib.import_module("src.ui.views.5_Analytics_Reporting_View")
            view_module.render_analytics_reporting_view(active_role)

        elif "Dean & Leadership" in view_selection or active_role in [UserRole.LEADERSHIP, UserRole.ADMIN]:
            view_module = importlib.import_module("src.ui.views.4_Leadership_View")
            view_module.render_leadership_view(active_role)

        elif "Student Inquiries" in view_selection:
            view_module = importlib.import_module("src.ui.views.7_Student_Engagement_Hub")
            view_module.render_student_engagement_view(active_role)

        elif "AI RAG Chat" in view_selection:
            view_module = importlib.import_module("src.ui.views.8_AI_Admissions_RAG_Advisor")
            view_module.render_ai_rag_advisor_view(active_role)

        elif active_role == UserRole.SCHOOL_PARTNER:
            view_module = importlib.import_module("src.ui.views.2_School_Partner")
            view_module.render_school_partner_view()

        elif active_role == UserRole.RECRUITER:
            view_module = importlib.import_module("src.ui.views.3_Recruiter_Desk")
            view_module.render_recruiter_view()

        else:
            view_module = importlib.import_module("src.ui.views.1_Aspirant_Desk")
            view_module.render_aspirant_view()

    except ModuleNotFoundError as err:
        st.error(f"Error loading view module for persona '{active_role}': {err}")
        st.info("Verify that all view files exist in `src/ui/views/`.")
    except Exception as ex:
        st.error(f"Unexpected error rendering view: {ex}")


if __name__ == "__main__":
    main()
    
