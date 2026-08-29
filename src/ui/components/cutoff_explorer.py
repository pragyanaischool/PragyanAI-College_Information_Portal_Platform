"""
src/ui/components/cutoff_explorer.py

Interactive KCET, COMEDK, and JEE Rank Cutoff Predictor and Filter component.
Provides:
- Parametric filter controls (Exam, Year, Branch, Category Quota, Rank)
- Admission feasibility classification (Safe, Moderate, Ambitious)
- Side-by-side college comparison card generator
- Robust DataFrame formatting with dynamic column renaming
"""

import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.db.repository import CollegeRepository


def render_cutoff_finder():
    """Renders the cutoff predictor, admission feasibility calculator, and comparison card."""
    st.subheader("🎯 Entrance Cutoff & Feasibility Predictor")
    st.caption(
        "Evaluate your admission probability based on multi-year cutoff trends and quota allocations."
    )

    # -------------------------------------------------------------------------
    # 1. Parameter Input Grid
    # -------------------------------------------------------------------------
    c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.4])
    with c1:
        exam = st.selectbox(
            "Entrance Exam:",
            ["KCET", "COMEDK"],
            index=0,
            key="cutoff_filter_exam",
        )
    with c2:
        year = st.selectbox(
            "Target Year:",
            [2026, 2025, 2024],
            index=0,
            key="cutoff_filter_year",
        )
    with c3:
        branch = st.selectbox(
            "Preferred Branch:",
            ["CSE", "AI-DS", "ISE", "ECE", "MECH"],
            index=0,
            key="cutoff_filter_branch",
        )
    with c4:
        category = st.selectbox(
            "Category Quota:",
            ["GM", "1G", "2A", "2B", "3A", "3B", "SC", "ST"],
            index=0,
            key="cutoff_filter_category",
        )
    with c5:
        user_rank = st.number_input(
            "Your Entrance Rank:",
            min_value=1,
            max_value=185000,
            value=3500,
            step=100,
            key="cutoff_filter_rank",
        )

    # -------------------------------------------------------------------------
    # 2. Feasibility Query Execution
    # -------------------------------------------------------------------------
    if st.button("🔍 Check Admission Feasibility", type="primary", use_container_width=True):
        with get_db() as db:
            repo = CollegeRepository(db)
            df_eligible = repo.find_eligible_colleges(
                exam=exam,
                branch=branch,
                category=category,
                student_rank=user_rank,
                year=year,
                limit=20,
            )

        if not df_eligible.empty:
            st.success(
                f"Found {len(df_eligible)} Qualifying Benchmark Institutions for Rank #{user_rank:,} "
                f"({exam} {year} - {category} - {branch})"
            )

            # Categorize admission certainty if cutoff_rank is present
            if "cutoff_rank" in df_eligible.columns:
                def categorize_feasibility(row):
                    cutoff = row["cutoff_rank"]
                    if user_rank <= cutoff * 0.8:
                        return "🟢 Very Safe"
                    elif user_rank <= cutoff:
                        return "🟡 Safe"
                    elif user_rank <= cutoff * 1.15:
                        return "🟠 Borderline / Round-3"
                    return "🔴 Ambitious"

                df_eligible["Admission Probability"] = df_eligible.apply(
                    categorize_feasibility, axis=1
                )

            # Formulate Clean Column Mapping (Explicit variable binding, no walrus operator)
            year_label = str(year)
            column_mapping = {
                "college_code": "Code",
                "college_name": "College Name",
                "city": "Location",
                "naac_grade": "NAAC",
                "naac_cgpa": "NAAC CGPA",
                "nirf_rank_2025": "NIRF Rank",
                "cutoff_rank": f"{year_label} Cutoff Rank",
                "mgmt_fee_cse_lakhs": "Mgmt Fee (LPA)",
                "mgmt_fee_lpa": "Mgmt Fee (LPA)",
                "median_ctc_lpa": "Median CTC (LPA)",
                "highest_ctc_lpa": "Highest CTC (LPA)",
            }

            rename_dict = {
                col: column_mapping[col]
                for col in df_eligible.columns
                if col in column_mapping
            }
            df_display = df_eligible.rename(columns=rename_dict)

            # Reorder columns for optimal readability if available
            preferred_order = [
                "Code",
                "College Name",
                "Location",
                f"{year_label} Cutoff Rank",
                "Admission Probability",
                "NIRF Rank",
                "NAAC",
                "Median CTC (LPA)",
                "Highest CTC (LPA)",
                "Mgmt Fee (LPA)",
            ]
            final_cols = [c for c in preferred_order if c in df_display.columns]
            remaining_cols = [c for c in df_display.columns if c not in final_cols]

            st.dataframe(
                df_display[final_cols + remaining_cols],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.warning(
                f"Your rank #{user_rank:,} exceeds standard Round-2 merit cutoffs for {branch} under quota {category}. "
                f"Consider checking related branches (e.g., AI-DS, ISE, ECE) or exploring Institutional Management Quota seats."
            )

    # -------------------------------------------------------------------------
    # 3. Side-by-Side Comparison Module
    # -------------------------------------------------------------------------
    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
    with st.expander("⚖️ Compare Two Colleges Side-by-Side (Fees, Placements & NAAC)"):
        with get_db() as db:
            repo = CollegeRepository(db)
            all_colleges = repo.get_all_colleges()

        if all_colleges:
            college_options = [f"{c.code} - {c.name}" for c in all_colleges]
            col_sel1, col_sel2 = st.columns(2)

            with col_sel1:
                sel1 = st.selectbox("Select College A:", college_options, index=0, key="cmp_col_a")
            with col_sel2:
                default_idx2 = 1 if len(college_options) > 1 else 0
                sel2 = st.selectbox("Select College B:", college_options, index=default_idx2, key="cmp_col_b")

            code1 = sel1.split(" - ")[0]
            code2 = sel2.split(" - ")[0]

            with get_db() as db:
                repo = CollegeRepository(db)
                col1_data = repo.get_college_by_code(code1)
                col2_data = repo.get_college_by_code(code2)

            if col1_data and col2_data:
                comparison_metrics = [
                    ("NIRF 2025 Rank", f"#{col1_data.nirf_rank_2025}", f"#{col2_data.nirf_rank_2025}"),
                    ("NAAC Grade & CGPA", f"{col1_data.naac_grade} ({col1_data.naac_cgpa})", f"{col2_data.naac_grade} ({col2_data.naac_cgpa})"),
                    ("Median CTC Package", f"₹{col1_data.median_ctc_lpa} LPA", f"₹{col2_data.median_ctc_lpa} LPA"),
                    ("Highest CTC Package", f"₹{col1_data.highest_ctc_lpa} LPA", f"₹{col2_data.highest_ctc_lpa} LPA"),
                    ("Mgmt Quota Fee (CSE)", f"₹{col1_data.mgmt_fee_cse_lakhs} Lakhs/yr", f"₹{col2_data.mgmt_fee_cse_lakhs} Lakhs/yr"),
                    ("Govt Quota Fee (CET)", f"₹{col1_data.govt_fee_cet_lakhs} Lakhs/yr", f"₹{col2_data.govt_fee_cet_lakhs} Lakhs/yr"),
                    ("COMEDK Fee", f"₹{col1_data.comedk_fee_lakhs} Lakhs/yr", f"₹{col2_data.comedk_fee_lakhs} Lakhs/yr"),
                    ("NBA Accredited Programs", f"{col1_data.nba_accredited_programs} Programs", f"{col2_data.nba_accredited_programs} Programs"),
                    ("Autonomous Status", "Yes" if col1_data.autonomous else "No", "Yes" if col2_data.autonomous else "No"),
                ]

                df_comparison = pd.DataFrame(
                    comparison_metrics,
                    columns=["Evaluation Parameter", col1_data.short_name, col2_data.short_name],
                )

                st.table(df_comparison)
