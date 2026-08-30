"""
src/ui/app.py

Main application entry point and dynamic RBAC page router for the
PragyanAI College Intelligence & Decision Portal.
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

    # Live Database Status Monitor
    is_db_connected = check_db_health()
    if is_db_connected:
        st.sidebar.caption("🟢 **Database Status:** Connected (Active)")
    else:
        st.sidebar.caption("🟡 **Database Status:** In-Memory / Standby Mode")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧭 Platform Navigation")

    # Universal navigation list available across all user roles
    view_options = [
        "💬 AI Decision Hub & Aspirant Desk",
        "🏛️ College Master Hub & Showcase",
        "📊 Institutional Analytics & Reports",
        "🏛️ Dean & Leadership Governance",
        "👥 Student Inquiries & Engagement",
        "🤖 AI RAG Chat & Profile Advisor",
    ]

    view_selection = st.sidebar.radio(
        "Select Portal View",
        view_options,
        key="main_navigation_selector"
    )

    # Dynamic Persona & Navigation View Routing
    try:
        if "College Master Hub" in view_selection:
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
    
