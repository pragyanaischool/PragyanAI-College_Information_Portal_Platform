"""
src/ui/app.py

Main application entry point and dynamic RBAC page router for the
PragyanAI College Intelligence & Decision Portal.
"""

import importlib
import os
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
    # Ensure all required folders exist (data/raw/, data/seed/, data/vector_store/)
    settings.ensure_directories()

    # Create all tables defined in SQLAlchemy models
    try:
        init_db()
    except Exception as exc:
        st.error(f"Database schema initialization notice: {exc}")
        return

    # Check whether the 'colleges' table exists and contains data
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

                # Generate seed CSV files if missing, then populate database
                generate_cutoffs_csv()
                generate_students_csv()
                seed_database()

    except Exception as e:
        st.warning(f"Notice during automatic database bootstrapping: {e}")


# -----------------------------------------------------------------------------
# 3. Main Application Flow
# -----------------------------------------------------------------------------
def main():
    # Streamlit Global Page Configuration
    st.set_page_config(
        page_title="PragyanAI College Intelligence Hub",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject CSS Theme Tokens & Metric Card Styling
    inject_custom_css()

    # Self-healing Application Initialization
    bootstrap_application()

    # Render Persona Switcher & Language Selector on Sidebar
    active_role = render_auth_sidebar()

    # Live Database Status Monitor
    is_db_connected = check_db_health()
    if is_db_connected:
        st.sidebar.caption(" **Database Status:** Connected (Active)")
    else:
        st.sidebar.caption(" **Database Status:** In-Memory / Standby Mode")

    # Dynamic Persona View Routing
    try:
        if active_role in [UserRole.GUEST.value, UserRole.ASPIRANT.value]:
            view_module = importlib.import_module("src.ui.views.1_Aspirant_Desk")
            view_module.render_aspirant_view()

        elif active_role == UserRole.SCHOOL_PARTNER.value:
            view_module = importlib.import_module("src.ui.views.2_School_Partner")
            view_module.render_school_partner_view()

        elif active_role == UserRole.RECRUITER.value:
            view_module = importlib.import_module("src.ui.views.3_Recruiter_Desk")
            view_module.render_recruiter_view()

        elif active_role == UserRole.LEADERSHIP.value:
            view_module = importlib.import_module("src.ui.views.4_Leadership_View")
            view_module.render_leadership_view()

        else:
            # Fallback default view
            view_module = importlib.import_module("src.ui.views.1_Aspirant_Desk")
            view_module.render_aspirant_view()

    except ModuleNotFoundError as err:
        st.error(f"Error loading view module for persona '{active_role}': {err}")
        st.info("Verify that all view files exist in `src/ui/views/`.")
    except Exception as ex:
        st.error(f"Unexpected error rendering view: {ex}")


if __name__ == "__main__":
    main()
