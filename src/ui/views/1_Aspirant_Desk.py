"""
src/ui/views/1_🎓_Aspirant_Desk.py

Student and Parent Aspirant Journey:
- Guided 5-Step Progress Pipeline Indicator
- Step 1: 📝 Multi-Test Score & Rank Profiler (KCET, COMEDK, JEE, Boards & Scorecard PDF OCR)
- Step 2: 🎯 Cutoff Profiler, City/Affiliation Types & Top Recommendations (+ 4-Year Educational ROI)
- Step 3: ⚖️ Side-by-Side College Comparison (Select from Recommended Matches)
- Step 4: 🏛️ Institutional Knowledge Directory, Verified Direct Portals & PDF Downloads
- Step 5: 🗣️ Voice of Stakeholders (Alumni, Students, Recruiters, Principal & HOD Quotes/Bites)
- Dedicated Counseling Desk: ✍️ Direct Admission Inquiry & Multi-Institution Selection
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
from src.ui.components.cutoff_explorer import (
    render_step1_score_input,
    render_step2_profiler_and_recommendations,
    render_step3_side_by_side_comparison,
    render_step4_knowledge_directory,
    render_step5_stakeholder_voices,
)
from src.ui.components.roi_charts import render_roi_analytics_dashboard
from src.ui.styles import inject_custom_css, render_metric_card


def render_step_progress_indicator(current_step: int = 1):
    """Renders a modern 5-step interactive progress tracker."""
    steps = [
        ("1", "Score Input", "Multi-Test Scores"),
        ("2", "Profiler & Match", "Fees & Top Matches"),
        ("3", "Compare Colleges", "Side-by-Side Matrix"),
        ("4", "Official Portals", "Direct Directories"),
        ("5", "Stakeholder Voices", "Alumni & Recruiter Bites"),
    ]

    cols = st.columns(5)
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
                    padding: 0.65rem;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
                    min-height: 85px;
                ">
                    <div style="
                        width: 24px; height: 24px;
                        background: {bg_color};
                        color: #ffffff;
                        border-radius: 50%;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 700;
                        font-size: 0.8rem;
                        margin-bottom: 0.2rem;
                    ">{badge}</div>
                    <div style="font-weight: 700; font-size: 0.82rem; color: #0f172a;">{title}</div>
                    <div style="font-size: 0.7rem; color: #64748b;">{subtitle}</div>
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
                Follow the 5-step guided path to evaluate admission cutoffs across multiple tests, benchmark institutional ROI, review verified fees, compare colleges, and secure counseling.
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
    # Tab Workspace Menu (5 Steps + Direct Counseling + AI Assistant)
    # -------------------------------------------------------------------------
    tab_step1, tab_step2, tab_step3, tab_step4, tab_step5, tab_lead, tab_ai = st.tabs([
        "📝 Step 1: Score Profiler",
        "🎯 Step 2: Recommendations & ROI",
        "⚖️ Step 3: Compare Colleges",
        "🏛️ Step 4: Official Portals & PDFs",
        "🗣️ Step 5: Stakeholder Voices",
        "✍️ Direct Counseling & Quota Lock",
        "🤖 Voice & Multimodal AI Guide",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Step 1 - Multi-Test Score & Rank Profiler
    # -------------------------------------------------------------------------
    with tab_step1:
        st.session_state.aspirant_journey_step = 1
        
        render_step1_score_input()

        # Optional Scorecard OCR / Text Extraction Card
        with st.expander("📄 Or upload your KCET / COMEDK Scorecard PDF for instant auto-read:", expanded=False):
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
                        st.info("Uploaded PDF is image-based. Your manually entered scores above will be utilized.")
                except Exception as e:
                    st.warning(f"Could not parse file: {e}")

        col_nav_1, col_nav_2 = st.columns([6, 1])
        with col_nav_2:
            if st.button("Next: View Match & ROI ➡️", key="btn_next_step2"):
                st.session_state.aspirant_journey_step = 2
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: Step 2 - Profiler, Affiliation Types, Fees & Top Matches + ROI Analytics
    # -------------------------------------------------------------------------
    with tab_step2:
        st.session_state.aspirant_journey_step = 2
        
        render_step2_profiler_and_recommendations()

        st.markdown("<br/>", unsafe_allow_html=True)
        # 4-Year Educational ROI Payback Curves
        render_roi_analytics_dashboard()

        col_nav_prev, col_nav_next = st.columns([1, 1])
        with col_nav_prev:
            if st.button("⬅️ Back to Step 1 (Scores)", key="btn_back_to_1"):
                st.session_state.aspirant_journey_step = 1
                st.rerun()
        with col_nav_next:
            if st.button("Next: Compare Side-by-Side ➡️", key="btn_next_step3"):
                st.session_state.aspirant_journey_step = 3
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: Step 3 - Compare Two Colleges Side-by-Side (From Recommendations)
    # -------------------------------------------------------------------------
    with tab_step3:
        st.session_state.aspirant_journey_step = 3
        
        # Side-by-side comparison pre-filled with top matches
        render_step3_side_by_side_comparison()

        col_nav_prev3, col_nav_next3 = st.columns([1, 1])
        with col_nav_prev3:
            if st.button("⬅️ Back to Step 2 (Recommendations)", key="btn_back_to_2"):
                st.session_state.aspirant_journey_step = 2
                st.rerun()
        with col_nav_next3:
            if st.button("Next: Official Portals & PDFs ➡️", key="btn_next_step4"):
                st.session_state.aspirant_journey_step = 4
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 4: Step 4 - Institutional Knowledge Directory, Direct Portals & PDFs
    # -------------------------------------------------------------------------
    with tab_step4:
        st.session_state.aspirant_journey_step = 4
        
        # Direct Web Portals Directory (Admissions, KEA matrix, Placements)
        render_step4_knowledge_directory()

        st.markdown("---")
        st.subheader("📥 Official Brochures, Fee Matrix & Campus Discovery")
        st.caption("Download institutional brochures and view virtual walkthroughs of Centers of Excellence.")

        col_docs, col_video = st.columns([1, 1])

        # Self-healing download handler
        settings.ensure_directories()
        flyer_path = settings.BROCHURES_DIR / "Admission_Flyer_2026.pdf"
        roi_path = settings.BROCHURES_DIR / "Placement_ROI_Report_2026.pdf"

        if not flyer_path.exists() or not roi_path.exists():
            generate_raw_documents()

        with col_docs:
            st.markdown("#### 📄 Verified Institutional Publications")
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
                "qualify for up to a 50% tuition scholarship under institutional quotas."
            )

        with col_video:
            st.markdown("#### 🎥 Virtual Labs & Campus Discovery Tour")
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        col_nav_prev4, col_nav_next4 = st.columns([1, 1])
        with col_nav_prev4:
            if st.button("⬅️ Back to Step 3 (Comparison)", key="btn_back_to_3"):
                st.session_state.aspirant_journey_step = 3
                st.rerun()
        with col_nav_next4:
            if st.button("Next: Stakeholder Voices ➡️", key="btn_next_step5"):
                st.session_state.aspirant_journey_step = 5
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 5: Step 5 - Voice of the Stakeholders (Alumni, Students, Recruiters, Leadership)
    # -------------------------------------------------------------------------
    with tab_step5:
        st.session_state.aspirant_journey_step = 5
        
        # Multimodal Stakeholder Perspectives with LinkedIn URLs, Video/Audio Bites & Statements
        render_step5_stakeholder_voices()

        col_nav_prev5, col_nav_next5 = st.columns([1, 1])
        with col_nav_prev5:
            if st.button("⬅️ Back to Step 4 (Portals)", key="btn_back_to_4"):
                st.session_state.aspirant_journey_step = 4
                st.rerun()
        with col_nav_next5:
            if st.button("Next: Connect with Admissions ➡️", key="btn_next_to_lead"):
                st.session_state.aspirant_journey_step = 5
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 6: Direct Counseling & Admission Lead Form (Multi-Target Support)
    # -------------------------------------------------------------------------
    with tab_lead:
        st.subheader("✍️ Lock In Direct Admission & Counseling Support")
        st.caption("Connect directly with the college admissions directorates for multi-institution seat allocation, scholarships, and fee concessions.")

        with st.form("aspirant_guided_lead_form"):
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                s_name = st.text_input("Candidate Full Name *", placeholder="e.g. Aarav Sharma")
                p_name = st.text_input("Parent / Guardian Name", placeholder="e.g. Ramesh Sharma")
                c_email = st.text_input("Contact Email Address *", placeholder="aarav@gmail.com")
            with c_f2:
                c_phone = st.text_input("Mobile / WhatsApp Number *", placeholder="+91 98450 12345")
                
                # Multi-institution target selection input
                target_colleges = st.multiselect(
                    "Target Institution (Select one or multiple colleges) *:",
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
                    default=["E001 - RV College of Engineering (RVCE)"],
                    help="You can select multiple target institutions for your admission inquiry.",
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
                if not s_name or not c_email or not c_phone or not target_colleges:
                    st.error("Please fill in all mandatory fields (*) and select at least one Target Institution.")
                else:
                    try:
                        with get_db() as db:
                            repo = CollegeRepository(db)
                            for col_str in target_colleges:
                                code_val = col_str.split(" - ")[0]
                                repo.create_admission_lead({
                                    "student_name": s_name,
                                    "parent_name": p_name,
                                    "contact_email": c_email,
                                    "contact_phone": c_phone,
                                    "target_college_code": code_val,
                                    "target_branch": target_branch,
                                    "admission_type": adm_type,
                                    "intent_score": 5 if "Management" in adm_type else 3,
                                    "query_notes": notes,
                                })
                        st.success(f"🎉 Admission inquiries for {len(target_colleges)} selected institution(s) have been successfully logged! The Admissions Directorate will contact you shortly.")
                    except Exception as err:
                        st.error(f"Error submitting inquiry: {err}")

    # -------------------------------------------------------------------------
    # TAB 7: Conversational Voice/Text AI Assistant
    # -------------------------------------------------------------------------
    with tab_ai:
        render_multimodal_chat()


if __name__ == "__main__":
    render_aspirant_view()
