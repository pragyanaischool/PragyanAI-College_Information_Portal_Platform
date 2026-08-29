"""
src/ui/views/1_🎓_Aspirant_Desk.py

Student and Parent Aspirant Desk: Cutoff Explorer, Fee Structure Flyers,
Multimodal AI Assistant, and Direct Admission Inquiry Form.
"""

import streamlit as st
from src.core.database import get_db
from src.db.repository import CollegeRepository
from src.ui.components.chat_interface import render_multimodal_chat
from src.ui.components.cutoff_explorer import render_cutoff_finder
from src.ui.components.roi_charts import render_roi_analytics_dashboard
from src.ui.styles import inject_custom_css, render_metric_card


def render_aspirant_view():
    inject_custom_css()

    st.title("🎓 Student & Parent Aspirant Desk")
    st.markdown("Explore verified entrance cutoffs, compare management quota fees, and evaluate 4-year placement ROI.")

    # High-level benchmark KPI metrics
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Benchmark Colleges", "15 Institutions", "All Autonomous")
    with k2:
        render_metric_card("Highest Placement", "62.0 LPA", "Tier-1 Product")
    with k3:
        render_metric_card("Computing Median CTC", "11.5 LPA", "+1.2 LPA YoY")
    with k4:
        render_metric_card("Average ROI Payback", "16 Months", "Full Investment Recovery")

    st.divider()

    # Cutoff Predictor Section
    render_cutoff_finder()

    st.divider()

    # ROI Analytics & Bubble Scatter Dashboard
    render_roi_analytics_dashboard()

    st.divider()

    # Download Official Assets & Direct Lead Inquiry
    col_assets, col_lead = st.columns([1, 1])

    with col_assets:
        st.subheader("📥 Official Brochures & Campus Tours")
        st.markdown("Download official, verified fee structures and view research facilities:")

        with open("data/raw/brochures/Admission_Flyer_2026.pdf", "rb") as f_brochure:
            st.download_button(
                "📄 Download Management Quota Fee Flyer (PDF)",
                data=f_brochure.read(),
                file_name="Management_Fee_Structure_2026.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with open("data/raw/brochures/Placement_ROI_Report_2026.pdf", "rb") as f_roi:
            st.download_button(
                "📈 Download 4-Year Salary ROI Report (PDF)",
                data=f_roi.read(),
                file_name="Placement_ROI_Report_2026.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    with col_lead:
        st.subheader("📩 Direct Admission & Counseling Inquiry")
        st.markdown("Submit your details to connect with the Institutional Admissions Desk:")

        with st.form("aspirant_lead_form"):
            s_name = st.text_input("Student Full Name *")
            p_name = st.text_input("Parent / Guardian Name")
            c_email = st.text_input("Contact Email Address *")
            c_phone = st.text_input("Mobile / WhatsApp Number *")

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                target_col = st.selectbox("Target College:", ["E001 - RVCE", "E002 - BMSCE", "E003 - MSRIT", "E004 - PESU", "E005 - DSCE"])
            with col_sub2:
                target_branch = st.selectbox("Preferred Branch:", ["CSE", "AI-DS", "ISE", "ECE", "MECH"])

            adm_type = st.radio("Admission Pathway:", ["Management Quota", "Merit CET/COMEDK Counseling", "Sports / NRI Quota"], horizontal=True)
            notes = st.text_area("Specific Queries (Fee Concession, Hostel, Cutoff Borderline):")

            if st.form_submit_button("Submit Admission Inquiry", type="primary", use_container_width=True):
                if not s_name or not c_email or not c_phone:
                    st.error("Please fill in all mandatory fields (*).")
                else:
                    with get_db() as db:
                        repo = CollegeRepository(db)
                        repo.create_admission_lead({
                            "student_name": s_name,
                            "parent_name": p_name,
                            "contact_email": c_email,
                            "contact_phone": c_phone,
                            "target_college_code": target_col.split(" - ")[0],
                            "target_branch": target_branch,
                            "admission_type": adm_type,
                            "intent_score": 5 if "Management" in adm_type else 3,
                            "query_notes": notes,
                        })
                    st.success("Your inquiry has been directly escalated to the Admissions Directorate!")

    st.divider()

    # Multimodal Voice/Text AI Assistant
    render_multimodal_chat()


if __name__ == "__main__":
    render_aspirant_view()
