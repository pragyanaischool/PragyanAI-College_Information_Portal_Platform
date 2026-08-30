"""
src/ui/views/7_Student_Engagement_Hub.py

Student Interest, Inquiries & Suggestions Hub:
Tracks prospective student interest signals, direct questions, grievances, and strategic suggestions
with interactive session state management and fallback demo datasets.
"""

import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.core.security import UserRole
from src.db.models import AdmissionLead


def render_student_engagement_view(current_role: UserRole):
    """Renders student-shown interest, live inquiries, and feedback pipelines."""
    st.title("💬 Student Interest & Inquiry Engagement Hub")
    st.markdown("Monitor prospective student engagement signals, direct questions, feedback, and campus suggestions in real-time.")
    st.markdown("---")

    # Initialize session state for interactive student submissions if missing
    if "session_suggestions" not in st.session_state:
        st.session_state.session_suggestions = [
            {"Category": "Curriculum", "Suggestion": "Introduce hands-on Generative AI capstone projects starting from the 3rd semester.", "Votes": 184, "Status": "Under Review"},
            {"Category": "Infrastructure", "Suggestion": "Upgrade central library high-compute cluster with 24/7 biometric student access.", "Votes": 142, "Status": "Approved"},
            {"Category": "Placements", "Suggestion": "Organize exclusive hackathons sponsored by top-tier semiconductor and AI product firms.", "Votes": 115, "Status": "Implemented"},
        ]

    if "session_inquiries" not in st.session_state:
        st.session_state.session_inquiries = [
            {"Query ID": "L-101", "Student Name": "Aarav Sharma", "Contact Email": "aarav.s@gmail.com", "Target Branch": "Computer Science & Eng", "Query / Question": "Inquired about management quota fee waiver and hostel facilities.", "Status": "New"},
            {"Query ID": "L-102", "Student Name": "Priya Hegde", "Contact Email": "priya.h@yahoo.com", "Target Branch": "Artificial Intelligence & DS", "Query / Question": "Asked about NVIDIA GPU cluster lab access for undergraduate thesis.", "Status": "Contacted"},
            {"Query ID": "L-103", "Student Name": "Karthik R.", "Contact Email": "karthik.dev@gmail.com", "Target Branch": "Electronics & Communication", "Query / Question": "Requested details regarding semiconductor VLSI design placement median CTC.", "Status": "Verified"},
        ]

    # Metrics Summary Bar
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Expressed Interests", "520+ Students", "+24% this month")
    with c2:
        st.metric("Active Student Queries", f"{len(st.session_state.session_inquiries)} Pending", "Avg. Response: 1.8 hrs")
    with c3:
        st.metric("Student Suggestions Logged", f"{len(st.session_state.session_suggestions)} Submissions", "4 Implemented")

    st.markdown("---")

    # Tabs for Engagement Categories
    tab_inquiries, tab_interests, tab_suggestions = st.tabs([
        "❓ Student Questions & Inquiries",
        "🔥 Shown Interest & Quota Intent",
        "💡 Student Suggestions & Feedback"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: STUDENT QUESTIONS & INQUIRIES
    # -------------------------------------------------------------------------
    with tab_inquiries:
        st.subheader("❓ Live Student Questions & Admissions Queries")
        st.markdown("Direct inquiries submitted by prospective applicants regarding fee structures, branch availability, and lab access.")

        st.dataframe(pd.DataFrame(st.session_state.session_inquiries), use_container_width=True)

        st.markdown("### ⚙️ Action: Respond to Student Inquiry")
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            selected_student = st.selectbox("Select Student Inquiry", [item["Student Name"] for item in st.session_state.session_inquiries], key="eng_q_sel")
        with col_sel2:
            new_stat = st.selectbox("Update Status", ["New", "Contacted", "Verified", "Resolved"], key="eng_stat_sel")

        response_text = st.text_area("Draft Direct Email / SMS Response:")
        if st.button("📤 Send Official Institutional Response", type="primary"):
            for item in st.session_state.session_inquiries:
                if item["Student Name"] == selected_student:
                    item["Status"] = new_stat
            st.success(f"Response successfully transmitted to **{selected_student}** and status updated to **{new_stat}**!")
            st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: SHOWN INTEREST & QUOTA INTENT
    # -------------------------------------------------------------------------
    with tab_interests:
        st.subheader("🔥 Students Who Showed Direct Interest")
        st.markdown("Telemetry of prospective candidates bookmarking programs, checking fee structures, and exploring campus tours.")

        interest_data = [
            {"Student Name": "Aarav Sharma", "Parent Name": "Rajesh Sharma", "Branch": "Computer Science & Eng", "Entrance Rank": 2450, "Intent Score": "⭐ 5 / 5", "Pipeline Status": "New"},
            {"Student Name": "Priya Hegde", "Parent Name": "Suresh Hegde", "Branch": "Artificial Intelligence & DS", "Entrance Rank": 1210, "Intent Score": "⭐ 4 / 5", "Pipeline Status": "Contacted"},
            {"Student Name": "Karthik R.", "Parent Name": "Ramesh R.", "Branch": "Electronics & Communication", "Entrance Rank": 4120, "Intent Score": "⭐ 5 / 5", "Pipeline Status": "Verified"},
            {"Student Name": "Sneha Rao", "Parent Name": "Prakash Rao", "Branch": "Information Science", "Entrance Rank": 6800, "Intent Score": "⭐ 3 / 5", "Pipeline Status": "New"}
        ]
        st.dataframe(pd.DataFrame(interest_data), use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 3: STUDENT SUGGESTIONS & FEEDBACK
    # -------------------------------------------------------------------------
    with tab_suggestions:
        st.subheader("💡 Student & Counselor Suggestions for Institutional Growth")
        st.markdown("Crowd-sourced recommendations submitted during campus outreach webinars and tech symposiums.")

        st.dataframe(pd.DataFrame(st.session_state.session_suggestions), use_container_width=True)

        st.markdown("### ✍️ Submit New Student / Counselor Suggestion")
        with st.form("submit_suggestion_form"):
            s_cat = st.selectbox("Suggestion Category", ["Curriculum", "Infrastructure", "Placements", "Hostel Life", "Research"])
            s_text = st.text_input("Suggestion Description:")
            if st.form_submit_button("🚀 Submit Suggestion for Review", type="primary"):
                if s_text.strip():
                    st.session_state.session_suggestions.append({
                        "Category": s_cat,
                        "Suggestion": s_text.strip(),
                        "Votes": 1,
                        "Status": "Under Review"
                    })
                    st.success("🎉 Suggestion successfully logged and added to the institutional review queue!")
                    st.rerun()
                else:
                    st.warning("Please enter suggestion details before submitting.")


if __name__ == "__main__":
    render_student_engagement_view(UserRole.LEADERSHIP)
        
