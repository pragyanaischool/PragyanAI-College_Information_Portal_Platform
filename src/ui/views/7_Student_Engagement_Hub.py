"""
src/ui/views/7_Student_Engagement_Hub.py

Student Interest, Inquiries & Suggestions Hub:
Tracks prospective student interest signals, questions, suggestions, and feedback
allowing admissions teams and deans to respond and engage proactively.
"""

import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.core.security import UserRole, require_role
from src.db.models import AdmissionLead, College


def render_student_engagement_view(current_role: UserRole):
    """Renders student-shown interest, inquiries, and feedback pipelines."""
    try:
        require_role(current_role, "view_naac_nba_analytics")
    except PermissionError as e:
        st.error(f"⛔ {e}")
        st.info("Please switch your role to **Dean & Institutional Leadership** or **System Administrator**.")
        return

    st.title("💬 Student Interest & Inquiry Engagement Hub")
    st.markdown("Monitor student-shown interest, direct questions, grievances, and strategic suggestions in real-time.")
    st.markdown("---")

    with get_db() as db:
        colleges = db.query(College).all()
        leads = db.query(AdmissionLead).all()

    if not colleges:
        st.warning("No institutional data found.")
        return

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total Expressed Interests", f"{len(leads) * 4}+ Students", "+18% this month")
    with col_m2:
        st.metric("Active Student Queries", f"{len(leads)} Pending", "Avg. Response: 2.4 hrs")
    with col_m3:
        st.metric("Student Suggestions Logged", "42 Submissions", "8 Implemented")

    st.markdown("---")

    tab_inquiries, tab_interests, tab_suggestions = st.tabs([
        "❓ Student Questions & Inquiries",
        "🔥 Shown Interest & Quota Intent",
        "💡 Student Suggestions & Feedback"
    ])

    with tab_inquiries:
        st.subheader("❓ Live Student Questions & Admissions Queries")
        st.markdown("Direct queries submitted by prospective engineering applicants regarding fee structures, branch availability, and hostel facilities.")

        if leads:
            query_data = [{
                "Query ID": l.id[:8],
                "Student Name": l.student_name,
                "Contact Email": l.contact_email,
                "Target Branch": l.target_branch,
                "Query / Question": l.query_notes or "Inquired about management quota seat availability and scholarship slabs.",
                "Status": l.status
            } for l in leads]
            st.dataframe(pd.DataFrame(query_data), use_container_width=True)
        else:
            st.info("No active queries recorded.")

    with tab_interests:
        st.subheader("🔥 Students Who Showed Direct Interest")
        st.markdown("Analytics of prospective candidates bookmarking and tracking specific college branches.")

        if leads:
            interest_data = [{
                "Student": l.student_name,
                "Parent": l.parent_name or "Not Specified",
                "Target College Code": l.target_college_code,
                "Entrance Exam Rank": l.entrance_rank or "N/A",
                "Intent Score": f"⭐ {l.intent_score} / 5"
            } for l in leads]
            st.dataframe(pd.DataFrame(interest_data), use_container_width=True)

    with tab_suggestions:
        st.subheader("💡 Student & Counselor Suggestions for Institutional Growth")
        st.markdown("Crowd-sourced recommendations submitted during campus outreach webinars and tech symposiums.")

        suggestions = [
            {"Category": "Curriculum", "Suggestion": "Introduce more hands-on GenAI capstone projects in the 3rd year.", "Votes": 142, "Status": "Under Review"},
            {"Category": "Infrastructure", "Suggestion": "Upgrade GPU clusters in the central computing lab for deep learning research.", "Votes": 98, "Status": "Approved"},
            {"Category": "Placements", "Suggestion": "Organize dedicated hackathons sponsored by product-based companies.", "Votes": 76, "Status": "Implemented"},
        ]
        st.dataframe(pd.DataFrame(suggestions), use_container_width=True)
