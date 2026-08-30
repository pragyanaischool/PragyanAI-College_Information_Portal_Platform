"""
src/ui/views/6_College_Master_Hub.py

College Master Hub & Institutional Showcase Portal:
Designed for students, recruiters, and college administrators with:
- Live Placement Statistics & CTC Stacks
- Centers of Excellence (COEs) & Advanced R&D Projects
- 360° Infrastructure Galleries (Campus, Labs, Classrooms, Events)
- Achiever Profiles (Faculty, Alumni, and Current Students with GitHub & LinkedIn)
- Industry-Aligned Curriculum, Skill Programs & Certification Blueprints
- Real-time College Admin Update & Editing Suite
"""

import streamlit as st
from src.core.database import get_db
from src.core.security import UserRole
from src.db.repository import CollegeRepository
from src.ui.styles import inject_custom_css, render_metric_card


def render_college_master_hub_view():
    inject_custom_css()

    st.title("🏛️ College Master Hub & Institutional Showcase")
    st.markdown("Explore verified institutional credentials, R&D breakthroughs, infrastructure galleries, achiever talent pools, and skill enhancement curricula designed for aspiring engineers and tier-1 recruiters.")

    # Fetch available colleges from database
    try:
        with get_db() as db:
            repo = CollegeRepository(db)
            colleges = repo.get_all_colleges()
    except Exception:
        colleges = []

    if not colleges:
        colleges = [
            {"code": "E001", "name": "RV College of Engineering (RVCE)", "city": "Bengaluru", "nirf_rank_2025": 38, "naac_grade": "A+", "median_ctc_lpa": 14.5, "highest_ctc_lpa": 55.0},
            {"code": "E002", "name": "BMS College of Engineering (BMSCE)", "city": "Bengaluru", "nirf_rank_2025": 72, "naac_grade": "A+", "median_ctc_lpa": 11.2, "highest_ctc_lpa": 48.0},
        ]

    # Helper function for safe attribute/key access
    def get_val(item, key, default):
        if hasattr(item, key):
            val = getattr(item, key)
            return val if val is not None else default
        elif isinstance(item, dict):
            return item.get(key, default)
        return default

    college_options = [f"{get_val(c, 'code', 'E000')} - {get_val(c, 'name', 'College')} ({get_val(c, 'city', 'City')})" for c in colleges]
    selected_col_str = st.selectbox("Select Institution to Inspect Master Showcase:", college_options, key="master_hub_college_select")
    selected_code = selected_col_str.split(" - ")[0]
    
    col_info = next((c for c in colleges if get_val(c, "code", "") == selected_code), colleges[0])

    # Header Metrics Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("NIRF 2025 Ranking", f"#{get_val(col_info, 'nirf_rank_2025', 50)}", "National Engineering Rank")
    with m2:
        render_metric_card("Median Placement CTC", f"₹{get_val(col_info, 'median_ctc_lpa', 10.0)} LPA", "Verified Annual Median")
    with m3:
        render_metric_card("Highest Package", f"₹{get_val(col_info, 'highest_ctc_lpa', 45.0)} LPA", "Top Multi-National Offer")
    with m4:
        render_metric_card("NAAC Accreditation", f"Grade {get_val(col_info, 'naac_grade', 'A+')}", "Highest Quality Mark")

    st.divider()

    # Determine available tabs based on user role
    user_role = st.session_state.get("user_role", UserRole.ASPIRANT)
    is_admin = user_role in [UserRole.ADMIN, UserRole.LEADERSHIP]
    
    if is_admin:
        tabs_list = [
            "📈 Placements & Events", 
            "🔬 COEs & Current R&D", 
            "🏛️ Campus, Labs & Class Views", 
            "🌟 Achiever Profiles",
            "🎓 Syllabus & Skill Programs",
            "🛠️ Admin: Update Details",
        ]
    else:
        tabs_list = [
            "📈 Placements & Events", 
            "🔬 COEs & Current R&D", 
            "🏛️ Campus, Labs & Class Views", 
            "🌟 Achiever Profiles",
            "🎓 Syllabus & Skill Programs",
        ]

    master_tabs = st.tabs(tabs_list)

    t_overview = master_tabs[0]
    t_coes = master_tabs[1]
    t_infra = master_tabs[2]
    t_achievers = master_tabs[3]
    t_syllabus = master_tabs[4]
    t_admin = master_tabs[5] if is_admin else None

    # =========================================================================
    # TAB 1: Placements, Highlights & Events
    # =========================================================================
    with t_overview:
        st.subheader("📈 Placement Highlights & Recent Institutional Events")
        st.caption(f"Comprehensive placement statistics and recent milestone events for {get_val(col_info, 'name', 'Institution')}.")

        p1, p2 = st.columns(2)
        with p1:
            st.markdown(
                """
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem;">
                    <h4 style="margin:0; color:#1e3a8a;">💼 Key Placement Highlights</h4>
                    <ul style="color:#334155; font-size:0.92rem; padding-left:1.2rem; margin-top:0.5rem;">
                        <li><b>94.5% Overall Placement Conversion Rate</b> across all engineering branches.</li>
                        <li><b>380+ Elite Recruiters</b> visiting campus annually (Microsoft, Google, Amazon, Qualcomm, Cisco).</li>
                        <li><b>Zero-Day Dream Offers</b> exceeding ₹30 LPA secured by over 120 students.</li>
                        <li><b>Global Internships</b> with stipend packages up to ₹1.5 Lakhs/month.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with p2:
            st.markdown(
                """
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem;">
                    <h4 style="margin:0; color:#1e3a8a;">🎉 Recent Institutional Events</h4>
                    <ul style="color:#334155; font-size:0.92rem; padding-left:1.2rem; margin-top:0.5rem;">
                        <li><b>Annual National Hackathon 2026:</b> 48-hour hackathon with ₹10 Lakhs prize pool.</li>
                        <li><b>Global AI & Semiconductor Symposium:</b> Keynotes by IEEE fellows and industry leaders.</li>
                        <li><b>Inter-Collegiate Robotics Championship:</b> Autonomous rover racing showcase.</li>
                        <li><b>Startup Incubation Demo Day:</b> 25 student-founded deep-tech ventures pitching to VCs.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 2: Centers of Excellence (COEs) & Current R&D
    # =========================================================================
    with t_coes:
        st.subheader("🔬 Centers of Excellence (COEs) & Flagship R&D Projects")
        st.caption("Advanced multi-disciplinary research facilities and grant-funded innovation testbeds on campus.")

        coe_list = [
            {"name": "NVIDIA AI & Generative RAG Innovation Center", "desc": "Equipped with 16x NVIDIA DGX stations for training large language models and multimodal vision models."},
            {"name": "Cadence VLSI Semiconductor Design CoE", "desc": "Industry-partnered semiconductor foundry testbed for ASIC tape-out and low-power chip verification."},
            {"name": "Electric Vehicle (EV) Powertrain & Battery R&D Lab", "desc": "Research center focusing on solid-state battery thermal management and autonomous battery management systems."},
            {"name": "Cyber-Threat Intelligence & Zero-Trust Lab", "desc": "DRDO and MeitY sponsored sandbox for advanced network security and cryptographic protocol testing."}
        ]

        for coe in coe_list:
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:1rem; margin-bottom:0.75rem; border-left:4px solid #2563eb;">
                    <h4 style="margin:0; color:#0f172a;">🏢 {coe['name']}</h4>
                    <p style="margin:0.3rem 0 0 0; color:#475569; font-size:0.9rem;">{coe['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 3: 360° Infrastructure Galleries (Campus, Labs, Class, Events)
    # =========================================================================
    with t_infra:
        st.subheader("🏛️ 360° Campus Infrastructure & Facilities Showcase")
        st.caption("Visual walkthrough of world-class campus grounds, high-tech research labs, smart lecture halls, and event auditoriums.")

        infra_tabs = st.tabs(["🌳 Campus View", "💻 Lab View", "🎓 Class View", "🏟️ Events View"])

        with infra_tabs[0]:
            st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=1000&q=80", caption="Main Academic Block & Central Library Plaza")
            st.markdown("Spread across 50+ acres of lush greenery, featuring high-speed Wi-Fi, 24/7 digital resource centers, and incubation hubs.")

        with infra_tabs[1]:
            st.image("https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=1000&q=80", caption="Advanced High-Compute GPU Research Laboratory")
            st.markdown("Dedicated computing labs equipped with high-end workstations, oscilloscope workbenches, and FPGA testing boards.")

        with infra_tabs[2]:
            st.image("https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1000&q=80", caption="Smart Tiered Lecture Hall with Hybrid AV Integration")
            st.markdown("Air-conditioned, acoustically optimized lecture halls with smart interactive displays and lecture recording streaming.")

        with infra_tabs[3]:
            st.image("https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=1000&q=80", caption="Main Auditorium hosting International Tech Symposia")
            st.markdown("State-of-the-art 2,000-seater auditorium hosting annual fests, technical conferences, and recruiter pre-placement talks.")

    # =========================================================================
    # TAB 4: Achiever Profiles (Faculty, Alumni, Students)
    # =========================================================================
    with t_achievers:
        st.subheader("🌟 Hall of Achievers: Faculty, Alumni & Student Spotlights")
        st.caption("Highlighting top-tier scholarly impact, global alumni leadership, and elite student developer profiles.")

        ach_tab1, ach_tab2, ach_tab3 = st.tabs(["👨‍🏫 Achiever Faculties", "🎓 Achiever Alumni", "👨‍🎓 Achiever Students"])

        with ach_tab1:
            st.markdown("#### 🔬 Distinguished Faculty Profiles")
            fac_profiles = [
                {"name": "Dr. Ramesh Kumar", "desig": "Professor & Head (CSE)", "pub": "85+ IEEE/ACM Publications, 3,200 Citations (h-index: 28)", "scholar": "https://scholar.google.com"},
                {"name": "Dr. Ananya Rao", "desig": "Professor & Head (AI-ML)", "pub": "Lead Investigator for MeitY Deep-Tech Grant, 18 Patents Filed", "scholar": "https://scholar.google.com"}
            ]
            for f in fac_profiles:
                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1rem; margin-bottom:0.75rem;">
                        <h4 style="margin:0; color:#1e3a8a;">{f['name']} <span style="font-size:0.85rem; color:#64748b; font-weight:normal;">({f['desig']})</span></h4>
                        <p style="margin:0.3rem 0 0 0; color:#334155; font-size:0.9rem;">{f['pub']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with ach_tab2:
            st.markdown("#### 🌟 Global Alumni Leaders")
            alumni_profiles = [
                {"name": "Arjun Sundaram", "role": "Staff AI Engineer @ Google Brain (Class of 2019)", "linkedin": "https://www.linkedin.com"},
                {"name": "Sneha Kulkarni", "role": "Silicon Design Engineer @ Qualcomm (Class of 2021)", "linkedin": "https://www.linkedin.com"}
            ]
            for a in alumni_profiles:
                c_a1, c_a2 = st.columns([3, 1])
                with c_a1:
                    st.markdown(f"**{a['name']}** — *{a['role']}*")
                with c_a2:
                    st.link_button("🔗 LinkedIn Profile", a['linkedin'], use_container_width=True)

        with ach_tab3:
            st.markdown("#### 🚀 Student Open-Source & Hackathon Achievers")
            student_profiles = [
                {"name": "Karthik Raja", "batch": "Final Year B.E. (AI-DS)", "bio": "Winner of National AI Hackathon 2025, Contributor to LangChain & LlamaIndex.", "github": "https://github.com", "linkedin": "https://linkedin.com"},
                {"name": "Pooja Hegde", "batch": "3rd Year B.E. (CSE)", "bio": "Published 2 papers in Springer IEEE on Computer Vision anomaly detection.", "github": "https://github.com", "linkedin": "https://linkedin.com"}
            ]
            for s in student_profiles:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:1rem; margin-bottom:0.75rem;">
                        <h4 style="margin:0; color:#0f172a;">{s['name']} <span style="font-size:0.85rem; color:#059669; font-weight:600;">({s['batch']})</span></h4>
                        <p style="margin:0.3rem 0 0.5rem 0; color:#334155; font-size:0.9rem;">{s['bio']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                b_g, b_l = st.columns(2)
                with b_g:
                    st.link_button("🐙 GitHub Profile", s['github'], use_container_width=True)
                with b_l:
                    st.link_button("🔗 LinkedIn Profile", s['linkedin'], use_container_width=True)

    # =========================================================================
    # TAB 5: Syllabus & Skill Programs
    # =========================================================================
    with t_syllabus:
        st.subheader("🎓 Industry-Aligned Curriculum, Syllabus & Skill Programs")
        st.caption("Review autonomous credit frameworks, elective structures, and mandatory multi-year technical skill bootcamps.")

        s1, s2 = st.columns(2)
        with s1:
            st.markdown(
                """
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem;">
                    <h4 style="margin:0; color:#1e3a8a;">📚 Autonomous Syllabus Structure</h4>
                    <ul style="color:#334155; font-size:0.92rem; padding-left:1.2rem; margin-top:0.5rem;">
                        <li><b>Bi-Annual Curriculum Revision</b> with 40% active industry participation.</li>
                        <li><b>Minor Specializations</b> in Artificial Intelligence, Quantum Computing, and Electric Vehicles.</li>
                        <li><b>Flexible Credit System</b> allowing multidisciplinary electives and audit courses.</li>
                        <li><b>Capstone Industrial Projects</b> spanning the final two semesters.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with s2:
            st.markdown(
                """
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem;">
                    <h4 style="margin:0; color:#1e3a8a;">🛠️ Mandatory Technical Skill Programs</h4>
                    <ul style="color:#334155; font-size:0.92rem; padding-left:1.2rem; margin-top:0.5rem;">
                        <li><b>Year 1:</b> Computational Problem Solving & Python Data Engineering.</li>
                        <li><b>Year 2:</b> Advanced Data Structures, Concurrency & Linux Systems.</li>
                        <li><b>Year 3:</b> Agentic AI, Generative RAG & Cloud Microservices.</li>
                        <li><b>Year 4:</b> Enterprise Software Architecture & Product Engineering.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 6: College Admin Update Details (Restricted to Authorized Admin/Leadership)
    # =========================================================================
    if t_admin is not None:
        with t_admin:
            st.subheader("🛠️ College Admin Portal: Update Institutional Details")
            st.caption(f"Modify verified placement metrics, R&D breakthroughs, and showcase highlights for {get_val(col_info, 'name', 'Institution')}.")

            with st.form("admin_college_update_form"):
                up_median = st.number_input("Update Median CTC (₹ LPA):", min_value=3.0, max_value=30.0, value=float(get_val(col_info, 'median_ctc_lpa', 12.0)), step=0.5)
                up_highest = st.number_input("Update Highest Package (₹ LPA):", min_value=10.0, max_value=100.0, value=float(get_val(col_info, 'highest_ctc_lpa', 50.0)), step=1.0)
                up_nirf = st.number_input("Update NIRF Rank:", min_value=1, max_value=500, value=int(get_val(col_info, 'nirf_rank_2025', 50)), step=1)
                
                up_statement = st.text_area("Principal / Directorate Statement:", value=get_val(col_info, 'principal_statement', 'Our mission is experiential education and outcome-based engineering excellence.'))

                if st.form_submit_button("💾 Save & Publish Institutional Updates", type="primary"):
                    try:
                        with get_db() as db:
                            from src.db.models import College
                            db_col = db.query(College).filter(College.code == selected_code).first()
                            if db_col:
                                db_col.median_ctc_lpa = up_median
                                db_col.highest_ctc_lpa = up_highest
                                db_col.nirf_rank_2025 = up_nirf
                                db_col.principal_statement = up_statement
                                db.commit()
                        st.success(f"🎉 Institutional showcase successfully updated for `{get_val(col_info, 'name', 'Institution')}`!")
                    except Exception as e:
                        st.error(f"Error saving updates: {e}")


if __name__ == "__main__":
    render_college_master_hub_view()
