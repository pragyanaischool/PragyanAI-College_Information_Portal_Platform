"""
src/ui/views/1_🎓_Aspirant_Desk.py

Student and Parent Aspirant Desk:
- High-level Institutional KPIs & Benchmarks
- Interactive Cutoff Finder & Scorecard Upload Parser
- Plotly 4-Year ROI & Salary Payback Curve
- Self-Healing Official Brochure & Report Downloads
- Direct Admission Inquiry & Escalation Form
- Multimodal Voice/Text Conversational AI Assistant
"""

import os
from pathlib import Path
import fitz  # PyMuPDF
import streamlit as st

from src.core.config import settings
from src.core.database import get_db
from src.db.generate_data_files import generate_raw_documents
from src.db.repository import CollegeRepository
from src.ui.components.chat_interface import render_multimodal_chat
from src.ui.components.cutoff_explorer import render_cutoff_finder
from src.ui.components.roi_charts import render_roi_analytics_dashboard
from src.ui.styles import inject_custom_css, render_metric_card


def render_aspirant_view():
    """Renders the Student and Parent Aspirant Desk."""
    inject_custom_css()

    st.title("🎓 Student & Parent Aspirant Desk")
    st.markdown(
        "Explore verified entrance cutoffs, compare management quota fees, "
        "and evaluate 4-year placement ROI across top engineering institutions."
    )

    # -------------------------------------------------------------------------
    # 1. High-Level Benchmark KPIs
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # 2. Entrance Cutoff Predictor & Optional Scorecard OCR/Text Parser
    # -------------------------------------------------------------------------
    render_cutoff_finder()

    with st.expander("📄 Have a scorecard PDF? Upload your KCET / COMEDK Rank Card (Optional)"):
        uploaded_scorecard = st.file_uploader(
            "Upload Scorecard PDF for instant rank extraction:",
            type=["pdf"],
            key="aspirant_scorecard_uploader",
        )
        if uploaded_scorecard is not None:
            try:
                # Read stream in memory
                doc = fitz.open(stream=uploaded_scorecard.read(), filetype="pdf")
                extracted_text = ""
                for page in doc:
                    extracted_text += page.get_text()
                doc.close()

                if extracted_text.strip():
                    st.success("Scorecard uploaded and parsed successfully!")
                    st.text_area(
                        "Extracted Rank & Candidate Details:",
                        extracted_text[:600] + ("..." if len(extracted_text) > 600 else ""),
                        height=120,
                    )
                else:
                    st.info("Uploaded PDF contains no extractable raw text (scanned image).")
            except Exception as e:
                st.warning(f"Could not parse scorecard PDF: {e}")

    st.divider()

    # -------------------------------------------------------------------------
    # 3. 4-Year Educational Investment vs. Salary ROI Curve
    # -------------------------------------------------------------------------
    render_roi_analytics_dashboard()

    st.divider()

    # -------------------------------------------------------------------------
    # 4. Verified Brochures, Campus Tours & Admission Lead Escalation
    # -------------------------------------------------------------------------
    col_assets, col_lead = st.columns([1, 1])

    # Left Column: Self-healing Brochure & Report Downloads
    with col_assets:
        st.subheader("📥 Official Brochures & Campus Tours")
        st.markdown("Download official, verified fee structures and explore research facilities:")

        # Ensure directory and files exist via absolute paths
        settings.ensure_directories()
        flyer_path = settings.BROCHURES_DIR / "Admission_Flyer_2026.pdf"
        roi_path = settings.BROCHURES_DIR / "Placement_ROI_Report_2026.pdf"

        # Self-healing fallback: Generate if missing
        if not flyer_path.exists() or not roi_path.exists():
            generate_raw_documents()

        if flyer_path.exists():
            with open(flyer_path, "rb") as f_brochure:
                st.download_button(
                    "📄 Download Management Quota Fee Flyer (PDF)",
                    data=f_brochure.read(),
                    file_name="Management_Fee_Structure_2026.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            st.warning("Admission flyer currently generating...")

        if roi_path.exists():
            with open(roi_path, "rb") as f_roi:
                st.download_button(
                    "📈 Download 4-Year Salary ROI Report (PDF)",
                    data=f_roi.read(),
                    file_name="Placement_ROI_Report_2026.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            st.warning("Salary ROI report currently generating...")

        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    # Right Column: Direct Admission Inquiry Form
    with col_lead:
        st.subheader("📩 Direct Admission & Counseling Inquiry")
        st.markdown("Submit your details to connect directly with the Institutional Admissions Desk:")

        with st.form("aspirant_lead_form"):
            s_name = st.text_input("Student Full Name *")
            p_name = st.text_input("Parent / Guardian Name")
            c_email = st.text_input("Contact Email Address *")
            c_phone = st.text_input("Mobile / WhatsApp Number *")

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                target_col = st.selectbox(
                    "Target College:",
                    [
                        "E001 - RVCE",
                        "E002 - BMSCE",
                        "E003 - MSRIT",
                        "E004 - PESU",
                        "E005 - DSCE",
                        "E006 - BIT",
                        "E008 - NIE",
                        "E010 - SIT",
                    ],
                )
            with col_sub2:
                target_branch = st.selectbox(
                    "Preferred Branch:",
                    ["CSE", "AI-DS", "ISE", "ECE", "MECH"],
                )

            adm_type = st.radio(
                "Admission Pathway:",
                ["Management Quota", "Merit CET/COMEDK Counseling", "Sports / NRI Quota"],
                horizontal=True,
            )
            notes = st.text_area("Specific Queries (Fee Concession, Hostel, Borderline Rank):")

            submit_lead = st.form_submit_button(
                "Submit Admission Inquiry",
                type="primary",
                use_container_width=True,
            )

            if submit_lead:
                if not s_name or not c_email or not c_phone:
                    st.error("Please fill in all mandatory fields (*).")
                else:
                    try:
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
                        st.success("Your inquiry has been logged and escalated to the Admissions Directorate!")
                    except Exception as err:
                        st.error(f"Error logging inquiry: {err}")

    st.divider()

    # -------------------------------------------------------------------------
    # 5. Multimodal Voice/Text Conversational AI Assistant
    # -------------------------------------------------------------------------
    render_multimodal_chat()


if __name__ == "__main__":
    render_aspirant_view()
