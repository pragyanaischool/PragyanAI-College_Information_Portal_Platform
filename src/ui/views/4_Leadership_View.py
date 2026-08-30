"""
src/ui/views/4_Leadership_View.py

Dean & Institutional Leadership Portal for PragyanAI College Intelligence Hub.
Provides executive visibility across institutional governance, comprehensive college profiles,
department-wise HOD/CoE intelligence, NAAC/NBA regulatory dossiers, and the Admissions CRM pipeline.
"""

import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.core.security import UserRole, require_role
from src.db.models import AdmissionLead, College, Department, Student


def render_leadership_view(current_role: UserRole):
    """Renders the executive institutional governance, college master details, and CRM portal."""
    try:
        require_role(current_role, "view_naac_nba_analytics")
    except PermissionError as e:
        st.error(f"⛔ {e}")
        st.info("Please switch your role to **Dean & Institutional Leadership** or **System Administrator** using the sidebar.")
        return

    st.title(" Institutional Governance & Leadership Intelligence")
    st.markdown(
        "Executive visibility across institutional profiles, department-wise CoE telemetry, "
        "NAAC/NBA regulatory frameworks, and high-intent admissions CRM pipelines."
    )
    st.markdown("---")

    # =========================================================================
    # 1. EXECUTIVE METRICS OVERVIEW
    # =========================================================================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Admissions Footfall", value="4,890 Leads", delta="+22% YoY")
    with col2:
        st.metric(label="High-Intent Mgmt Inquiries", value="640 Conversions", delta="+15% YoY")
    with col3:
        st.metric(label="NAAC Institutional CGPA", value="3.78 / 4.0", delta="A++ Grade Cycle-4")
    with col4:
        st.metric(label="NBA Tier-1 Programs", value="14 Accredited", delta="Valid up to 2028")

    st.markdown("---")

    # =========================================================================
    # 2. SELECT TAB SECTIONS
    # =========================================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. Overall College Master Hub",
        "2. Department-Wise Intelligence",
        "3. Admissions CRM & Lead Funnel",
        "4. NAAC & NBA Regulatory Dossiers"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: OVERALL COLLEGE MASTER HUB
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader(" Comprehensive Institutional Profiles & Governance")
        
        with get_db() as db:
            colleges = db.query(College).all()
            if not colleges:
                st.warning("No institutional records found in the database. Run `python -m src.db.seed_runner`.")
                return

            college_names = [c.name for c in colleges]
            selected_college_name = st.selectbox("Select Institution for Audit", college_names, key="lead_col_sel")
            college = next((c for c in colleges if c.name == selected_college_name), colleges[0])

        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.markdown(f"### {college.name} (`{college.short_name}`)")
            st.markdown(f" **Location:** {college.address}, {college.city}, {college.state}")
            st.markdown(f" **Year of Establishment:** {college.established_year} | **Type:** {'Private Autonomous' if college.autonomous else 'Affiliated Non-Autonomous'}")
            st.markdown(f" **Total Annual Intake:** {college.intake_total} Seats across UG/PG")
            
            st.markdown("####  Vision & Mission")
            st.info(f"**Vision:** {getattr(college, 'vision', 'Leadership in quality technical education and sustainable innovation.')}")
            st.success(f"**Mission:** {getattr(college, 'mission', 'Deliver outcome-based learning and foster industry partnerships.')}")

        with col_b:
            st.markdown("####  Accreditation & Ranking")
            st.metric("NAAC Grade & CGPA", f"{college.naac_grade} ({college.naac_cgpa}/4.0)")
            st.metric("NIRF National Rank (2025)", f"Rank #{college.nirf_rank_2025}")
            st.metric("NBA Accredited Programs", f"{college.nba_accredited_programs} Programs")

        st.markdown("####  Growth & Institutional Achievements")
        st.write(
            f"Over decades of academic excellence, **{college.short_name}** has transitioned into a premier "
            "deep-tech hub. Recognized for pioneering R&D grants from DST and AICTE, the institution maintains an "
            f"impressive placement median of **₹{college.median_ctc_lpa} LPA** with peak offers reaching **₹{college.highest_ctc_lpa} LPA**."
        )

        st.markdown("####  Official Institutional & Admission Brochures")
        col_pdf1, col_pdf2, col_pdf3 = st.columns(3)
        with col_pdf1:
            st.download_button(
                " Download Admission Flyer",
                data=b"Sample PDF content for admission flyer",
                file_name=f"{college.short_name}_Admission_Flyer_2026.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col_pdf2:
            st.download_button(
                " Download NAAC SSR Summary",
                data=b"Sample PDF content for NAAC audit",
                file_name=f"{college.short_name}_NAAC_SSR_Summary.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col_pdf3:
            st.download_button(
                " Download Placement & ROI Report",
                data=b"Sample PDF content for ROI report",
                file_name=f"{college.short_name}_Placement_ROI_2026.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # -------------------------------------------------------------------------
    # TAB 2: DEPARTMENT-WISE INTELLIGENCE
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader(" Department-Wise HOD, CoE & Talent Telemetry")
        
        with get_db() as db:
            departments = db.query(Department).filter(Department.college_code == college.code).all()
            if not departments:
                st.info(f"No specific department records indexed for {college.name}.")
            else:
                dept_names = [d.branch_name for d in departments]
                selected_dept_name = st.selectbox("Select Department / Branch", dept_names, key="lead_dept_sel")
                dept = next((d for d in departments if d.branch_name == selected_dept_name), departments[0])

                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown(f"####  HOD & Leadership: {dept.branch_name}")
                    st.write(f"**Head of Department:** {dept.hod_name or 'Dr. Department Chair'}")
                    st.info(dept.hod_statement or 'Committed to rigorous engineering and computational problem solving.')
                    st.markdown(f"**Approved Intake:** {dept.intake} Seats | **Research Labs:** {dept.labs_count}")
                    st.markdown(f"**Sponsored Research Grants:** ₹{dept.funded_grants_lakhs} Lakhs | **Patents Filed:** {dept.patents_filed}")

                with col_d2:
                    st.markdown("#### Centres of Excellence (CoEs)")
                    coes = dept.centers_of_excellence or ["AI & High Performance Computing Lab", "Cloud Native Systems Testbed"]
                    for coe in coes:
                        st.markdown(f"- {coe}")

                    st.markdown("####  Skill Programs & Bootcamps")
                    skills = dept.skill_programs or ["Generative AI & LLM Orchestration", "Advanced Systems Programming"]
                    for skill in skills:
                        st.markdown(f"- 💡 {skill}")

                st.markdown("---")
                col_d3, col_d4 = st.columns(2)
                with col_d3:
                    st.markdown("####  Notable Alumni Profiles")
                    alumni = dept.notable_alumni or ["Aarav Sharma (Founder, DeepTech AI)", "Neha Rao (Principal Engineer, Microsoft)"]
                    for alm in alumni:
                        st.markdown(f"- 🎓 {alm}")

                with col_d4:
                    st.markdown("#### 1. Department Events & Symposiums")
                    st.markdown("- 2. Annual National Coding Hackathon *'InnoHack'*")
                    st.markdown("- 3. AI/ML Inter-College Research Symposium")
                    st.markdown("- 4. Industry Expert Tech-Talk & Alumni Fireside Chat")

                st.markdown("####  Current Performing Students & Hackathon Winners")
                top_students = db.query(Student).filter(
                    Student.college_code == college.code,
                    Student.branch == dept.branch_code
                ).order_by(Student.cgpa.desc()).limit(5).all()

                if top_students:
                    student_data = [{
                        "USN": s.usn,
                        "Name": s.full_name,
                        "CGPA": s.cgpa,
                        "Hackathons Won": s.hackathons_won,
                        "Placement Status": s.placement_status,
                        "Offered CTC (LPA)": s.offered_ctc_lpa,
                        "Company": s.placed_company
                    } for s in top_students]
                    st.dataframe(pd.DataFrame(student_data), use_container_width=True)
                else:
                    st.info("No active student records found for this department branch.")

    # -------------------------------------------------------------------------
    # TAB 3: ADMISSIONS CRM & LEAD FUNNEL
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader(" Prospective Parent & Student Admission Leads")
        st.markdown("Live feed of escalated inquiries, entrance ranks, and quota selections requiring administrative follow-up.")

        with get_db() as db:
            leads = db.query(AdmissionLead).all()
            if not leads:
                st.info("No admission leads recorded in the CRM yet.")
            else:
                lead_data = [{
                    "Lead ID": l.id,
                    "Student Name": l.student_name,
                    "Parent Name": l.parent_name,
                    "Email": l.contact_email,
                    "Phone": l.contact_phone,
                    "Target College": l.target_college_code,
                    "Branch": l.target_branch,
                    "Admission Type": l.admission_type,
                    "Rank": l.entrance_rank,
                    "Intent Score": f"⭐ {l.intent_score} / 5",
                    "Status": l.status,
                    "Notes": l.query_notes
                } for l in leads]
                st.dataframe(pd.DataFrame(lead_data), use_container_width=True)

                st.markdown("###  Quick Lead Status Update")
                selected_lead_id = st.selectbox("Select Lead ID to Update", [l.id for l in leads])
                new_status = st.selectbox("New Pipeline Status", ["New", "Contacted", "Verified", "Enrolled"])
                if st.button("Update Lead Status", type="primary"):
                    lead_to_update = db.query(AdmissionLead).filter(AdmissionLead.id == selected_lead_id).first()
                    if lead_to_update:
                        lead_to_update.status = new_status
                        db.commit()
                        st.success(f"Lead status updated to **{new_status}** successfully!")
                        st.rerun()

    # -------------------------------------------------------------------------
    # TAB 4: NAAC & NBA REGULATORY DOSSIERS
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader(" NAAC SSR & NBA Outcome-Based Education Compliance")
        st.markdown(
            "Review criterion-level scores, Washington Accord PO1-PO12 attainment thresholds, "
            "and faculty Ph.D. cadre ratios."
        )

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("####  NAAC Criterion Summary (Cycle 4)")
            naac_df = pd.DataFrame([
                {"Criterion": "Criterion 1: Curricular Aspects", "Weightage": 150, "Score Awarded": 142},
                {"Criterion": "Criterion 2: Teaching-Learning & Evaluation", "Weightage": 200, "Score Awarded": 188},
                {"Criterion": "Criterion 3: Research, Innovations & Extension", "Weightage": 250, "Score Awarded": 235},
                {"Criterion": "Criterion 4: Infrastructure & Learning Resources", "Weightage": 100, "Score Awarded": 94},
                {"Criterion": "Criterion 5: Student Support & Progression", "Weightage": 130, "Score Awarded": 122},
            ])
            st.dataframe(naac_df, use_container_width=True)

        with col_r2:
            st.markdown("####  NBA Tier-1 OBE Outcome Attainment")
            nba_df = pd.DataFrame([
                {"Program Outcome": "PO1: Engineering Knowledge", "Threshold": "75%", "Attainment Level": "88.5%"},
                {"Program Outcome": "PO2: Problem Analysis", "Threshold": "75%", "Attainment Level": "82.0%"},
                {"Program Outcome": "PO3: Design / Development", "Threshold": "70%", "Attainment Level": "79.4%"},
                {"Program Outcome": "PO4: Investigations", "Threshold": "70%", "Attainment Level": "81.2%"},
                {"Program Outcome": "PO12: Life-Long Learning", "Threshold": "80%", "Attainment Level": "91.0%"},
            ])
            st.dataframe(nba_df, use_container_width=True)

        st.markdown("---")
        st.download_button(
            " Export NAAC & NBA Compliance Summary Report (CSV)",
            data=naac_df.to_csv(index=False).encode('utf-8'),
            file_name="NAAC_NBA_Compliance_Report_2026.csv",
            mime="text/csv"
        )
        
