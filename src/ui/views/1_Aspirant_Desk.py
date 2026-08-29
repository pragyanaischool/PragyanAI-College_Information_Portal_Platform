"""
src/ui/views/1_🎓_Aspirant_Desk.py

Student and Parent Aspirant Journey:
- Guided Step-by-Step Progress Pipeline
- Tabbed Navigation Workspace (Discovery, Cutoffs & Matching, ROI Analytics, Counselor Connect)
- Interactive Feasibility Calculator & Scorecard PDF OCR
- 4-Year Educational ROI Payback Curves
- Direct Admission Inquiry & Seat Reservation
- Multimodal Voice-Enabled College AI Assistant
"""

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


def render_step_progress_indicator(current_step: int = 1):
    """Renders a modern interactive step tracker."""
    steps = [
        ("1", "Explore Cutoffs", "Rank & Branch Matching"),
        ("2", "Compare Fees & ROI", "4-Year Salary Payback"),
        ("3", "Review Brochures", "Official Seat Matrix"),
        ("4", "Direct Counseling", "Seat Allocation & Contact"),
    ]

    cols = st.columns(4)
    for idx, (num, title, subtitle) in enumerate(steps):
        step_num = idx + 1
        with cols[idx]:
            if step_num < current_step:
                bg_color = "#10b981"  # Completed Green
                badge = "✓"
                border_style = "2px solid #10b981"
            elif step_num == current_step:
                bg_color = "#2563eb"  # Active Blue
                badge = num
                border_style = "2px solid #2563eb"
            else:
                bg_color = "#94a3b8"  # Upcoming Grey
                badge = num
                border_style = "1px dashed #cbd5e1"

            st.markdown(
                f"""
                <div style="
                    background: #ffffff;
                    border: {border_style};
                    border-radius: 10px;
                    padding: 0.75rem;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
                    min-height: 85px;
                ">
                    <div style="
                        width: 26px; height: 26px;
                        background: {bg_color};
                        color: #ffffff;
                        border-radius: 50%;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 700;
                        font-size: 0.85rem;
                        margin-bottom: 0.25rem;
                    ">{badge}</div>
                    <div style="font-weight: 700; font-size: 0.85rem; color: #0f172a;">{title}</div>
                    <div style="font-size: 0.72rem; color: #64748b;">{subtitle}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_aspirant_view():
    """Renders the Step-by-Step Aspirant Journey UI."""
    inject_custom_css()

    # Header Title Banner
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h1 style="margin-bottom: 0.2rem; color: #0f172a; font-weight: 800; font-size: 1.85rem;">
                🎓 Student & Parent Decision Gateway
            </h1>
            <p style="color: #64748b; font-size: 0.95rem; margin-top: 0;">
                Follow the 4-step guided path to evaluate admission cutoffs, benchmark institutional ROI, review verified fees, and secure counseling.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize Session Step State
    if "aspirant_journey_step" not in st.session_state:
        st.session_state.aspirant_journey_step = 1

    # Render Step Progress Bar
    render_step_progress_indicator(current_step=st.session_state.aspirant_journey_step)
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # High-level Quick Stats
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Benchmark Colleges", "15 Institutions", "All Autonomous Tier-1")
    with m2:
        render_metric_card("Highest Placement", "62.0 LPA", "Tier-1 Product")
    with m3:
        render_metric_card("Average Computing CTC", "11.5 LPA", "+1.2 LPA YoY")
    with m4:
        render_metric_card("Median ROI Payback", "16 Months", "Full Investment Recovery")

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Tab Workspace Menu
    # -------------------------------------------------------------------------
    tab_cutoffs, tab_roi, tab_brochures, tab_lead, tab_ai = st.tabs([
        "🎯 1. Cutoff Predictor & Matcher",
        "📊 2. ROI & Salary Analytics",
        "📥 3. Verified Seat Matrix & PDFs",
        "✍️ 4. Direct Counseling & Quota Lock",
        "🤖 5. Voice & Multimodal AI Guide",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Cutoff Matcher & Feasibility Wizard
    # -------------------------------------------------------------------------
    with tab_cutoffs:
        st.session_state.aspirant_journey_step = 1
        st.subheader("🎯 Step 1: Discover Your Qualifying Colleges & Branches")
        st.caption("Enter your entrance rank or upload your scorecard PDF for instant qualification filtering.")

        # Optional Scorecard OCR / Text Extraction Card
        with st.expander("📄 Have a scorecard PDF? Upload your KCET / COMEDK Rank Card for autofill", expanded=False):
            uploaded_scorecard = st.file_uploader(
                "Upload Scorecard (PDF):",
                type=["pdf"],
                key="scorecard_wizard_uploader",
            )
            if uploaded_scorecard is not None:
                try:
                    doc = fitz.open(stream=uploaded_scorecard.read(), filetype="pdf")
                    extracted_text = "".join([page.get_text() for page in doc])
                    doc.close()

                    if extracted_text.strip():
                        st.success("✅ Rank card parsed successfully!")
                        st.text_area(
                            "Extracted Scorecard Summary:",
                            extracted_text[:450] + ("..." if len(extracted_text) > 450 else ""),
                            height=90,
                        )
                    else:
                        st.info("Uploaded PDF is image-based. Please select your rank manually below.")
                except Exception as e:
                    st.warning(f"Could not parse file: {e}")

        # Interactive Cutoff Search
        render_cutoff_finder()

        col_nav_1, col_nav_2 = st.columns([6, 1])
        with col_nav_2:
            if st.button("Next: View ROI ➡️", key="btn_next_roi"):
                st.session_state.aspirant_journey_step = 2
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: ROI & Financial Payback Analytics
    # -------------------------------------------------------------------------
    with tab_roi:
        st.session_state.aspirant_journey_step = 2
        st.subheader("📊 Step 2: 4-Year Educational Fee vs. Placement Return")
        st.caption("Quantitative ROI model assessing 4-year tuition investments against first-year median salary packages.")

        render_roi_analytics_dashboard()

        col_nav_prev, col_nav_next = st.columns([1, 1])
        with col_nav_prev:
            if st.button("⬅️ Back to Cutoffs", key="btn_back_cutoffs"):
                st.session_state.aspirant_journey_step = 1
                st.rerun()
        with col_nav_next:
            if st.button("Next: Download Brochures ➡️", key="btn_next_brochures"):
                st.session_state.aspirant_journey_step = 3
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: Verified Brochures & Virtual Campus Tour
    # -------------------------------------------------------------------------
    with tab_brochures:
        st.session_state.aspirant_journey_step = 3
        st.subheader("📥 Step 3: Verified Fee Structures & Campus Infrastructure")
        st.caption("Download institutional brochures and view virtual walkthroughs of Centers of Excellence.")

        col_docs, col_video = st.columns([1, 1])

        # Self-healing download handler
        settings.ensure_directories()
        flyer_path = settings.BROCHURES_DIR / "Admission_Flyer_2026.pdf"
        roi_path = settings.BROCHURES_DIR / "Placement_ROI_Report_2026.pdf"

        if not flyer_path.exists() or not roi_path.exists():
            generate_raw_documents()

        with col_docs:
            st.markdown("#### 📄 Institutional Publications")
            if flyer_path.exists():
                with open(flyer_path, "rb") as f_brochure:
                    st.download_button(
                        "📄 Download Management Quota Fee Flyer (PDF)",
                        data=f_brochure.read(),
                        file_name="Management_Fee_Structure_2026.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            if roi_path.exists():
                with open(roi_path, "rb") as f_roi:
                    st.download_button(
                        "📈 Download 4-Year Salary ROI Report (PDF)",
                        data=f_roi.read(),
                        file_name="Placement_ROI_Report_2026.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            st.info(
                "💡 **Merit Concession Note:** Top 2,000 KCET & Top 1,500 COMEDK rank holders "
                "qualify for a 50% tuition scholarship under institutional quotas."
            )

        with col_video:
            st.markdown("#### 🎥 Virtual Labs & Campus Discovery")
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        col_nav_prev3, col_nav_next3 = st.columns([1, 1])
        with col_nav_prev3:
            if st.button("⬅️ Back to ROI", key="btn_back_roi"):
                st.session_state.aspirant_journey_step = 2
                st.rerun()
        with col_nav_next3:
            if st.button("Next: Connect with Admissions ➡️", key="btn_next_lead"):
                st.session_state.aspirant_journey_step = 4
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 4: Direct Counseling & Admission Lead Form
    # -------------------------------------------------------------------------
    with tab_lead:
        st.session_state.aspirant_journey_step = 4
        st.subheader("✍️ Step 4: Lock In Direct Admission & Counseling Support")
        st.caption("Connect directly with the college admissions directorate for seat allocation, scholarships, and fee concessions.")

        with st.form("aspirant_guided_lead_form"):
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                s_name = st.text_input("Candidate Full Name *", placeholder="e.g. Aarav Sharma")
                p_name = st.text_input("Parent / Guardian Name", placeholder="e.g. Ramesh Sharma")
                c_email = st.text_input("Contact Email Address *", placeholder="aarav@gmail.com")
            with c_f2:
                c_phone = st.text_input("Mobile / WhatsApp Number *", placeholder="+91 98450 12345")
                target_col = st.selectbox(
                    "Target Institution:",
                    [
                        "E001 - RV College of Engineering (RVCE)",
                        "E002 - BMS College of Engineering (BMSCE)",
                        "E003 - Ramaiah Institute of Technology (MSRIT)",
                        "E004 - PES University (PESU)",
                        "E005 - Dayananda Sagar College of Engineering (DSCE)",
                        "E006 - Bangalore Institute of Technology (BIT)",
                        "E008 - The National Institute of Engineering (NIE)",
                        "E010 - Siddaganga Institute of Technology (SIT)",
                    ],
                )
                target_branch = st.selectbox(
                    "Target Branch of Choice:",
                    ["CSE", "AI-DS", "ISE", "ECE", "MECH"],
                )

            adm_type = st.radio(
                "Preferred Admission Pathway:",
                ["Management Quota (Direct Seat Lock)", "Merit Counseling (KCET/COMEDK)", "Sports / NRI Sponsorship"],
                horizontal=True,
            )
            notes = st.text_area(
                "Specific Inquiries (Borderline Rank, Fee Concessions, Hostel Accommodation):",
                placeholder="Mention your entrance rank and any specific queries for the admissions desk...",
            )

            submit_inquiry = st.form_submit_button(
                "🚀 Submit Inquiry & Request Direct Callback",
                type="primary",
                use_container_width=True,
            )

            if submit_inquiry:
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
                        st.success("🎉 Your admission inquiry has been logged! The Admissions Directorate will contact you shortly.")
                    except Exception as err:
                        st.error(f"Error submitting inquiry: {err}")

    # -------------------------------------------------------------------------
    # TAB 5: Conversational Voice/Text AI Assistant
    # -------------------------------------------------------------------------
    with tab_ai:
        render_multimodal_chat()


if __name__ == "__main__":
    render_aspirant_view()
