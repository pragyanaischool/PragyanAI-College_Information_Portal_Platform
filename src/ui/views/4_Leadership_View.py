"""
src/ui/views/4_🏛️_Leadership_View.py

Dean & Institutional Leadership Dashboard: High-Intent Admission Leads CRM,
NAAC SSR Attainment, NBA Tier-1 Audit, and Outreach Conversion Metrics.
"""

import streamlit as st
from src.core.database import get_db
from src.db.repository import CollegeRepository
from src.ui.styles import inject_custom_css, render_metric_card


def render_leadership_view():
    inject_custom_css()

    st.title("🏛️ Institutional Governance & Leadership Intelligence")
    st.markdown("Executive visibility across admission lead funnels, NAAC Self-Study metrics, NBA OBE outcomes, and partner school outreach.")

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

    tab_crm, tab_accred = st.tabs(["📋 Admissions CRM & Lead Funnel", "📜 NAAC & NBA Regulatory Dossiers"])

    # Tab 1: Lead CRM
    with tab_crm:
        st.subheader("Prospective Parent & Student Admission Leads")
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

    # Tab 2: Accreditation & Compliance
    with tab_accred:
        st.subheader("Regulatory Compliance & Criterion-Wise Self-Study Reports")
        c_n1, c_n2 = st.columns(2)

        with c_n1:
            st.markdown("#### 📑 NAAC Self-Study Report (SSR)")
            st.markdown("Criterion 1-7 executive audit covering Curricular Agility, Ph.D. faculty ratio, and sponsored R&D grants.")
            with open("data/raw/regulatory/NAAC_Self_Study_Summary.pdf", "rb") as f_naac:
                st.download_button(
                    "📥 Download NAAC SSR Executive Summary (PDF)",
                    data=f_naac.read(),
                    file_name="NAAC_SSR_Summary_2026.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        with c_n2:
            st.markdown("#### 📑 NBA Tier-1 Compliance Report")
            st.markdown("Washington Accord Tier-1 evaluation, PO1-PO12 attainment thresholds, and faculty cadre retention audits.")
            with open("data/raw/regulatory/NBA_Criteria_Compliance_Report.pdf", "rb") as f_nba:
                st.download_button(
                    "📥 Download NBA OBE Compliance Dossier (PDF)",
                    data=f_nba.read(),
                    file_name="NBA_Compliance_Dossier_2026.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )


if __name__ == "__main__":
    render_leadership_view()
