"""
src/ui/components/cutoff_explorer.py

Interactive KCET, COMEDK, and JEE Rank Cutoff Predictor and Filter component.
"""

import streamlit as st
from src.core.database import get_db
from src.db.repository import CollegeRepository


def render_cutoff_finder():
    """Renders the cutoff predictor and admission feasibility calculator."""
    st.subheader("🎯 Entrance Cutoff & Feasibility Predictor")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        exam = st.selectbox("Entrance Exam:", ["KCET", "COMEDK"], index=0)
    with c2:
        branch = st.selectbox("Preferred Branch:", ["CSE", "AI-DS", "ISE", "ECE", "MECH"], index=0)
    with c3:
        category = st.selectbox("Category Quota:", ["GM", "1G", "2A", "2B", "3A", "3B", "SC", "ST"], index=0)
    with c4:
        user_rank = st.number_input("Your Entrance Rank:", min_value=1, max_value=185000, value=3500, step=100)

    if st.button("🔍 Check Admission Feasibility", type="primary", use_container_width=True):
        with get_db() as db:
            repo = CollegeRepository(db)
            df_eligible = repo.find_eligible_colleges(
                exam=exam,
                branch=branch,
                category=category,
                student_rank=user_rank,
                year=2026,
                limit=10,
            )

        if not df_eligible.empty:
            st.success(f"Found {len(df_eligible)} Qualifying Benchmark Institutions for Rank #{user_rank:,} ({exam} - {category})")
            
            # Format display dataframe
            df_display = df_eligible.rename(
                columns={
                    "college_name": "College Name",
                    "city": "Location",
                    "naac_grade": "NAAC",
                    "nirf_rank_2025": "NIRF Rank",
                    "cutoff_rank": f"{year_str := '2026'} Cutoff Rank",
                    "mgmt_fee_lpa": "Mgmt Fee (LPA)",
                    "median_ctc_lpa": "Median CTC (LPA)",
                    "highest_ctc_lpa": "Highest CTC (LPA)",
                }
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Your rank #{user_rank:,} exceeds the standard merit cutoff for {branch} under {category}. Consider Institutional Management Quota options below.")
