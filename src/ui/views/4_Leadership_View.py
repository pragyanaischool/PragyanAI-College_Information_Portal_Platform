"""
src/ui/views/4_Leadership_View.py

Dean & Institutional Leadership Dashboard: High-Intent Admission Leads CRM,
NAAC SSR Attainment, NBA Tier-1 Audit, and Multimodal Document Ingestion Portal.
"""

from pathlib import Path
import streamlit as st

from src.core.config import settings
from src.core.database import get_db
from src.db.generate_data_files import generate_raw_documents
from src.db.repository import CollegeRepository
from src.ui.components.file_uploader import render_document_uploader
from src.ui.styles import inject_custom_css, render_metric_card


def render_leadership_view():
    """Renders the Dean & Institutional Leadership Desk."""
    inject_custom_css()

    st.title(" Institutional Governance & Leadership Intelligence")
    st.markdown(
        "Executive visibility across admission lead funnels, NAAC Self-Study metrics, "
        "NBA OBE outcomes, and knowledge base document management."
    )

    # -------------------------------------------------------------------------
    # 1. Executive KPIs
    # -------------------------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Total Admissions Footfall", "4,890 Leads", "+22% YoY")
    with k2:
        render_metric_card("High-Intent Mgmt Inquiries", "640 Conversions", "+15% YoY")
    with k3:
        render_metric_card("NAAC Institutional CGPA", "3.78 / 4.0", "A++ Grade Cycle-4")
    with k4:
        render_metric_card("NBA Tier-1 Programs", "14 Accredited", "Valid up to 2028")

    st.divider()

    # -------------------------------------------------------------------------
    # 2. Main Tab Navigation
    # -------------------------------------------------------------------------
    tab_crm, tab_accred, tab_upload = st.tabs([
        "1. Admissions CRM & Lead Funnel",
        "2. NAAC & NBA Regulatory Dossiers",
        "3. Ingest Documents & Update RAG",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Admissions CRM & Lead Funnel
    # -------------------------------------------------------------------------
    with tab_crm:
        st.subheader("Prospective Parent & Student Admission Leads")
        st.caption("Live feed of escalated inquiries, entrance ranks, and quota selections.")

        with get_db() as db:
            repo = CollegeRepository(db)
            df_leads = repo.get_admission_leads()

        if not df_leads.empty:
            st.dataframe(
                df_leads.rename(
                    columns={
                        "student_name": "Student Name",
                        "parent_name": "Parent Name",
                        "contact_email": "Email",
                        "contact_phone": "Phone",
                        "target_college_code": "College",
                        "target_branch": "Target Branch",
                        "admission_type": "Quota",
                        "entrance_rank": "Rank",
                        "intent_score": "Intent (1-5)",
                        "status": "Lead Status",
                        "created_at": "Logged Date",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No admission leads recorded yet.")

    # -------------------------------------------------------------------------
    # TAB 2: Regulatory Compliance & Reports
    # -------------------------------------------------------------------------
    with tab_accred:
        st.subheader("Regulatory Compliance & Criterion-Wise Self-Study Reports")
        c_n1, c_n2 = st.columns(2)

        # Self-healing check: Ensure files exist before serving download buttons
        naac_path = settings.REGULATORY_DIR / "NAAC_Self_Study_Summary.pdf"
        nba_path = settings.REGULATORY_DIR / "NBA_Criteria_Compliance_Report.pdf"

        if not naac_path.exists() or not nba_path.exists():
            generate_raw_documents()

        with c_n1:
            st.markdown("####  NAAC Self-Study Report (SSR)")
            st.markdown(
                "Criterion 1-7 executive audit covering Curricular Agility, "
                "Ph.D. faculty ratio, and sponsored R&D grants."
            )
            if naac_path.exists():
                with open(naac_path, "rb") as f_naac:
                    st.download_button(
                        " Download NAAC SSR Executive Summary (PDF)",
                        data=f_naac.read(),
                        file_name="NAAC_SSR_Summary_2026.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
            else:
                st.warning("NAAC SSR document unavailable.")

        with c_n2:
            st.markdown("####  NBA Tier-1 Compliance Report")
            st.markdown(
                "Washington Accord Tier-1 evaluation, PO1-PO12 attainment thresholds, "
                "and faculty cadre retention audits."
            )
            if nba_path.exists():
                with open(nba_path, "rb") as f_nba:
                    st.download_button(
                        " Download NBA OBE Compliance Dossier (PDF)",
                        data=f_nba.read(),
                        file_name="NBA_Compliance_Dossier_2026.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
            else:
                st.warning("NBA compliance document unavailable.")

    # -------------------------------------------------------------------------
    # TAB 3: Dynamic Document Uploader & RAG Ingestion
    # -------------------------------------------------------------------------
    with tab_upload:
        render_document_uploader()


if __name__ == "__main__":
    render_leadership_view()
