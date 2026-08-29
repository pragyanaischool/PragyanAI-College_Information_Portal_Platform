"""
src/ui/components/roi_charts.py

Interactive Plotly analytics dashboard for Salary ROI, Fee Comparisons, and Placement Density.
"""

import plotly.express as px
import streamlit as st
from src.core.database import get_db
from src.db.repository import CollegeRepository


def render_roi_analytics_dashboard():
    """Renders comparative scatter plots and placement return visualizations."""
    st.subheader("📊 4-Year Educational Investment vs. Salary ROI Curve")

    with get_db() as db:
        repo = CollegeRepository(db)
        df_colleges = repo.get_colleges_summary_dataframe()

    if df_colleges.empty:
        st.info("No college benchmark metrics available.")
        return

    fig = px.scatter(
        df_colleges,
        x="mgmt_fee_cse_lakhs",
        y="median_ctc_lpa",
        size="highest_ctc_lpa",
        color="naac_grade",
        hover_name="name",
        hover_data=["city", "nirf_rank_2025", "highest_ctc_lpa"],
        labels={
            "mgmt_fee_cse_lakhs": "Management Quota Annual Fee (Lakhs INR)",
            "median_ctc_lpa": "Median Placement CTC (LPA)",
            "naac_grade": "NAAC Grade",
            "highest_ctc_lpa": "Highest Placement Offer (LPA)",
        },
        title="College ROI Analysis: Annual Fee vs. Median Placement Package (Bubble size = Peak Offer)",
    )

    fig.update_layout(
        template="plotly_white",
        hoverlabel=dict(bgcolor="white", font_size=12),
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)
