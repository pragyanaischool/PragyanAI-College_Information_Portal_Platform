"""
src/ui/views/3_💼_Recruiter_Desk.py

Corporate Recruiter Portal: Verified 1,050+ Student Talent Search,
Center of Excellence (CoE) R&D lookup, and Placement Analytics.
"""

import streamlit as st
from src.core.database import get_db
from src.db.repository import CollegeRepository
from src.ui.styles import inject_custom_css, render_metric_card


def render_recruiter_view():
    inject_custom_css()

    st.title("💼 Corporate Recruiter & Industry Partner Desk")
    st.markdown("Search verified undergraduate talent, explore Center of Excellence (CoE) R&D projects, and assess placement statistics.")

    # Talent KPIs
    with get_db() as db:
        repo = CollegeRepository(db)
        metrics = repo.get_placement_metrics()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Verified Talent Pool", f"{metrics['total_students']:,} Students", "15 Autonomous Colleges")
    with k2:
        render_metric_card("Overall Placement Rate", f"{metrics['placement_rate_pct']}%", "Active 2026 Batch")
    with k3:
        render_metric_card("Average Placement CTC", f"{metrics['average_ctc_lpa']} LPA", "Across all disciplines")
    with k4:
        render_metric_card("Peak CTC Package", f"{metrics['highest_ctc_lpa']} LPA", "SuperDream Product Tier")

    st.divider()

    tab_search, tab_coe = st.tabs(["🔍 Search Verified Candidate Talent", "🔬 Centers of Excellence & Research Labs"])

    # Tab 1: Talent Search Engine
    with tab_search:
        st.subheader("Filter Candidates by Technical Competencies & Academic Scores")
        c1, c2, c3 = st.columns(3)
        with c1:
            skill_query = st.selectbox(
                "Primary Technical Capability:",
                ["All", "LangChain", "PyTorch", "VLSI", "Kubernetes", "Embedded C", "TensorFlow", "React.js"],
            )
        with c2:
            min_cgpa = st.slider("Minimum CGPA Benchmark:", 6.0, 9.8, 7.5, step=0.1)
        with c3:
            status = st.selectbox("Placement Status:", ["All", "Placed", "Seeking", "Higher Studies"])

        with get_db() as db:
            repo = CollegeRepository(db)
            df_talent = repo.search_students_by_skills(
                skill_keyword=skill_query,
                min_cgpa=min_cgpa,
                placement_status=status,
                limit=300,
            )

        st.markdown(f"**Found {len(df_talent)} matching student profiles:**")
        st.dataframe(
            df_talent.rename(
                columns={
                    "usn": "USN",
                    "full_name": "Candidate Name",
                    "college_name": "Institution",
                    "branch": "Branch",
                    "cgpa": "CGPA",
                    "hackathons_won": "Hackathons",
                    "primary_skills": "Verified Skills",
                    "placement_status": "Status",
                    "offered_ctc_lpa": "CTC (LPA)",
                    "placed_company": "Company",
                    "linkedin_url": "LinkedIn Profile",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    # Tab 2: Centers of Excellence & Research
    with tab_coe:
        st.subheader("Institutional R&D Facilities & Corporate Sponsored Labs")
        with open("data/raw/presentations/COE_and_Department_Infrastructure.pptx", "rb") as f_pptx:
            st.download_button(
                "📊 Download Complete CoE Labs & Facility Presentation (PPTX)",
                data=f_pptx.read(),
                file_name="CoE_Research_Facilities_2026.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )

        st.markdown("""
        * **Center of Excellence in Generative AI & HPC:** NVIDIA H100 GPU compute clusters, sponsored by DST and industry partners.
        * **Semiconductor VLSI Design & Verification Suite:** Cadence Virtuoso and Synopsys toolchains for RISC-V SoC testing.
        * **Robotics & Cyber-Physical Systems Lab:** Drone flight arenas and 6-axis industrial robot testbeds in collaboration with Bosch.
        """)


if __name__ == "__main__":
    render_recruiter_view()
