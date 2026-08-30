"""
src/ui/views/5_Analytics_Reporting_View.py

Institutional Analytics & Cross-Campus Comparative Reporting Portal.
Provides advanced filtering, cutoff trends, placement salary comparisons, and exportable data reports.
"""

import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.core.security import UserRole, require_role
from src.db.models import College, Cutoff, Student
from src.ui.styles import inject_custom_css, render_metric_card


def render_analytics_reporting_view(current_role: UserRole):
    """Renders institutional analytics, cutoff trends, and comparative evaluation dashboards."""
    inject_custom_css()
    try:
        require_role(current_role, "view_placement_analytics")
    except PermissionError as e:
        st.error(f"⛔ {e}")
        st.info("Please switch your role to **Corporate Recruiter**, **Dean & Institutional Leadership**, or **System Administrator** using the sidebar.")
        return

    st.title("📊 Institutional Analytics & Comparative Reporting")
    st.markdown(
        "Multi-variable benchmarking across entrance exam cutoffs, placement CTC distributions, "
        "and departmental return on investment (ROI)."
    )
    st.markdown("---")

    with get_db() as db:
        colleges = db.query(College).all()
        cutoffs = db.query(Cutoff).all()
        students = db.query(Student).all()

    if not colleges:
        st.warning("No institutional data found in database. Run `python -m src.db.seed_runner`.")
        return

    # =========================================================================
    # 1. ANALYTICS METRICS OVERVIEW
    # =========================================================================
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Benchmarked Institutions", f"{len(colleges)} Colleges", "Statewide Top-Tier")
    with c2:
        avg_median_ctc = sum([c.median_ctc_lpa or 0 for c in colleges]) / len(colleges)
        render_metric_card("Average Median CTC", f"₹{round(avg_median_ctc, 1)} LPA", "Across Computing & Core")
    with c3:
        render_metric_card("Analyzed Student Talent Pool", f"{len(students)}+ Records", "Verified Placement Status")

    st.markdown("---")

    # =========================================================================
    # 2. ANALYTICS TABS
    # =========================================================================
    tab_cutoffs, tab_placements, tab_export = st.tabs([
        "📈 Cutoff Rank Trends",
        "💼 Placement Salary Benchmarking",
        "📥 Export Institutional Reports"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: CUTOFF RANK TRENDS
    # -------------------------------------------------------------------------
    with tab_cutoffs:
        st.subheader("🔍 Entrance Exam Cutoff Rank Analyzer (KCET & COMEDK)")
        st.markdown("Inspect historical and projected cutoff ranks across institutions, engineering branches, and reservation categories.")

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            exam_filter = st.selectbox("Exam Type", ["KCET", "COMEDK"], key="analytics_exam_sel")
        with col_f2:
            year_filter = st.selectbox("Academic Year", [2026, 2025, 2024], key="analytics_yr_sel")
        with col_f3:
            branch_filter = st.selectbox("Branch", ["CSE", "AI-DS", "ISE", "ECE", "MECH"], key="analytics_br_sel")
        with col_f4:
            category_filter = st.selectbox("Category Quota", ["All", "GM", "1G", "2A", "2B", "3A", "3B", "SC", "ST"], key="analytics_cat_sel")

        filtered_cutoffs = [
            c for c in cutoffs 
            if c.exam == exam_filter 
            and c.year == year_filter 
            and c.branch == branch_filter
            and (category_filter == "All" or c.category == category_filter)
        ]

        if filtered_cutoffs:
            df_cut = pd.DataFrame([{
                "College Code": c.college_code,
                "College Name": c.college_name,
                "Exam": c.exam,
                "Year": c.year,
                "Branch": c.branch,
                "Category": c.category,
                "Cutoff Rank": c.cutoff_rank
            } for c in filtered_cutoffs])
            st.dataframe(df_cut.sort_values(by="Cutoff Rank"), use_container_width=True)
        else:
            st.info("No matching cutoff records found for the selected filter combination.")

    # -------------------------------------------------------------------------
    # TAB 2: PLACEMENT SALARY BENCHMARKING
    # -------------------------------------------------------------------------
    with tab_placements:
        st.subheader("💼 Cross-College Placement CTC Distribution")
        st.markdown("Comparative evaluation of median and peak compensation packages across benchmark engineering colleges.")

        df_col = pd.DataFrame([{
            "College Code": c.code,
            "Short Name": c.short_name,
            "City": c.city,
            "NIRF Rank": c.nirf_rank_2025,
            "Median CTC (LPA)": c.median_ctc_lpa,
            "Highest CTC (LPA)": c.highest_ctc_lpa,
            "NAAC Grade": c.naac_grade
        } for c in colleges])

        st.dataframe(df_col.sort_values(by="NIRF Rank"), use_container_width=True)

        st.markdown("#### 📊 Median CTC Comparison Chart")
        st.bar_chart(df_col.set_index("Short Name")["Median CTC (LPA)"])

    # -------------------------------------------------------------------------
    # TAB 3: EXPORT INSTITUTIONAL REPORTS
    # -------------------------------------------------------------------------
    with tab_export:
        st.subheader("📥 Export Master Institutional Dataset")
        st.markdown("Download comprehensive CSV summaries for offline analysis, research evaluations, and administrative board presentations.")

        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            df_col_export = pd.DataFrame([{
                "Code": c.code,
                "Name": c.name,
                "City": c.city,
                "NAAC Grade": c.naac_grade,
                "NIRF Rank": c.nirf_rank_2025,
                "Median CTC LPA": c.median_ctc_lpa,
                "Highest CTC LPA": c.highest_ctc_lpa
            } for c in colleges])
            
            csv_colleges = df_col_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Download College Benchmarks CSV",
                data=csv_colleges,
                file_name="PragyanAI_College_Benchmarks_2026.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_ex2:
            df_student_export = pd.DataFrame([{
                "USN": s.usn,
                "Name": s.full_name,
                "College Code": s.college_code,
                "Branch": s.branch,
                "CGPA": s.cgpa,
                "Status": s.placement_status,
                "Offered CTC LPA": s.offered_ctc_lpa,
                "Company": s.placed_company
            } for s in students])

            csv_students = df_student_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="🎓 Download Student Talent Pool CSV",
                data=csv_students,
                file_name="PragyanAI_Student_Talent_Pool_2026.csv",
                mime="text/csv",
                use_container_width=True
            )
