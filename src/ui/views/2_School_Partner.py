"""
src/ui/views/2_🏫_School_Partner.py

School & PU College Partner Desk: Bulk Student Enrollment, Free AI Bootcamps,
Verifiable E-Certificate Generator, Live Webinar Schedules, Event Media Galleries, 
and Student-College Q&A Insights.
"""

import streamlit as st
from src.core.database import get_db
from src.db.repository import CollegeRepository
from src.ui.styles import inject_custom_css, render_metric_card
from src.utils.certificate_gen import generate_event_certificate


def render_school_partner_view():
    inject_custom_css()

    st.title("🏫 High School & PU College Outreach Partner Desk")
    st.markdown("Enroll classroom cohorts for free emerging technology masterclasses, track STEM student diagnostics, and explore interactive event galleries.")

    # High-level Metrics Banner
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Active Partner Schools", "52 PU Colleges", "+8 this quarter")
    with m2:
        render_metric_card("Students Upskilled", "4,850+ Students", "100% Free Access")
    with m3:
        render_metric_card("Bootcamp Tracks", "5 Specialized Tracks", "AI, Robotics, VLSI")
    with m4:
        render_metric_card("E-Certificates Issued", "3,920 Credentials", "Digitally Verified")

    st.divider()

    # Navigation Tabs
    t_reg, t_cert, t_webinars, t_gallery = st.tabs([
        "📝 Bulk Cohort & STEM Diagnostics", 
        "🎓 Student E-Certificates", 
        "📅 Live Webinars & PragyanAI Events", 
        "📸 Event Media & Student Feedback"
    ])

    # =========================================================================
    # TAB 1: Bulk School Cohort Registration & Detailed STEM Diagnostics
    # =========================================================================
    with t_reg:
        st.subheader("📝 Institutional Cohort Registration & STEM Profile Diagnostics")
        st.caption("Provide comprehensive school demographic data, science student strengths, and student engineering interest profiles.")

        with st.form("school_bulk_reg_form"):
            st.markdown("#### 🏫 1. Institution & Coordinator Details")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                school_name = st.text_input("School / Pre-University College Name *", placeholder="e.g. National Public School")
                city = st.text_input("City / District *", placeholder="e.g. Bengaluru Urban")
                coord_name = st.text_input("Coordinator / Principal Name *", placeholder="e.g. Dr. Rajesh Sharma")
            with col_s2:
                coord_email = st.text_input("Official Email Address *", placeholder="principal@npsblr.edu.in")
                coord_phone = st.text_input("Contact Phone Number *", placeholder="+91 98450 12345")
                batch_size = st.slider("Total Science / STEM Enrolled Students Across Grades:", 25, 1000, 150)

            st.markdown("---")
            st.markdown("#### 🔬 2. Student Tech Preferences & Engineering Aspirations")
            
            # Select desired technology streams
            tech_streams = st.multiselect(
                "Primary Technology Streams Students Are Interested In:",
                ["Artificial Intelligence & Machine Learning", "Internet of Things & Robotics", "Semiconductor VLSI Design", "Cloud Computing & Cybersecurity", "Full-Stack Software Development"],
                default=["Artificial Intelligence & Machine Learning", "Internet of Things & Robotics"]
            )

            # Preferred Engineering College Target Types
            target_college_types = st.multiselect(
                "Engineering College Categories Students Want to Target:",
                ["Tier-1 Autonomous Institutes (RVCE, BMSCE, MSRIT)", "Private State Universities (PESU, DSCE)", "Government Engineering Colleges (UVCE, KSRCT)"],
                default=["Tier-1 Autonomous Institutes (RVCE, BMSCE, MSRIT)"]
            )

            c_sub1, c_sub2 = st.columns(2)
            with c_sub1:
                program = st.selectbox(
                    "Select Featured Free Bootcamp / Masterclass Track:",
                    [
                        "Free Generative AI & Prompt Engineering 2-Day Bootcamp",
                        "IoT & Robotics Discovery Lab Session",
                        "Engineering Stream Selector & Career Aptitude Test",
                        "KCET & COMEDK Option Entry Strategy Session",
                        "Semiconductor VLSI & FPGA Prototyping Workshop",
                    ],
                )
            with c_sub2:
                counseling_interest = st.selectbox(
                    "Primary Student Admission Counseling Interest:",
                    ["Engineering Entrance Exam Strategy (KCET/COMEDK/JEE)", "Direct Management Quota & Scholarship Guidance", "Global Career & Tech Mentorship Pathways"],
                )

            mou = st.checkbox("Our institution is interested in signing a continuous PragyanAI STEM Outreach MOU.")

            if st.form_submit_button("🚀 Confirm Institutional Batch & Diagnostics Registration", type="primary"):
                if not school_name or not coord_email or not coord_phone:
                    st.error("Please fill in all mandatory school coordination fields (*).")
                else:
                    try:
                        with get_db() as db:
                            repo = CollegeRepository(db)
                            payload = {
                                "school_name": school_name,
                                "city": city,
                                "coordinator_name": coord_name,
                                "coordinator_email": coord_email,
                                "coordinator_phone": coord_phone,
                                "registered_batch_size": batch_size,
                                "selected_program": program,
                                "tech_streams": ", ".join(tech_streams),
                                "target_colleges": ", ".join(target_college_types),
                                "counseling_focus": counseling_interest,
                                "mou_signed": mou,
                            }
                            if hasattr(repo, "register_partner_school"):
                                repo.register_partner_school(payload)
                            else:
                                from src.db.models import AdmissionLead
                                lead = AdmissionLead(
                                    student_name=coord_name,
                                    parent_name=school_name,
                                    contact_email=coord_email,
                                    contact_phone=coord_phone,
                                    target_college_code=city,
                                    target_branch=program,
                                    admission_type="School Partner Cohort & Diagnostics",
                                    intent_score=5,
                                    query_notes=f"STEM Batch: {batch_size} | Streams: {tech_streams} | Counseling: {counseling_interest}"
                                )
                                db.add(lead)
                                db.commit()
                        st.success(f"🎉 Institutional profile registered successfully! Onboarding kits and diagnostic reports dispatched to `{coord_email}`.")
                    except Exception as e:
                        st.error(f"Error registering cohort: {e}")

    # =========================================================================
    # TAB 2: Verifiable E-Certificate Generator
    # =========================================================================
    with t_cert:
        st.subheader("🎓 Issue Verifiable E-Certificates for Attended Cohorts")
        st.caption("Generate official PDF certificates for students who successfully completed PragyanAI bootcamps and workshops.")

        with st.form("cert_form"):
            c_name = st.text_input("Student Full Name *:")
            c_school = st.text_input("Institution Name:", value="National Public School")
            c_event = st.selectbox(
                "Masterclass / Bootcamp Attended:",
                [
                    "Generative AI, RAG & Agentic AI using LangGraph",
                    "Hands-On Robotics, Autonomous Rovers & Micro-Sensors",
                    "Semiconductor VLSI, RTL Design & FPGA Prototyping",
                    "Engineering Stream Selector & Career Aptitude Masterclass",
                ],
            )
            if st.form_submit_button("Generate Official Landscape Certificate (PDF)", type="primary"):
                if c_name:
                    try:
                        cert_bytes = generate_event_certificate(
                            student_name=c_name,
                            event_title=c_event,
                            institution_name=c_school,
                        )
                        st.download_button(
                            label="📥 Download Generated Certificate (PDF)",
                            data=cert_bytes.getvalue(),
                            file_name=f"Certificate_{c_name.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                        )
                        st.success("✅ Certificate compiled and verified successfully!")
                    except Exception as e:
                        st.error(f"Error generating certificate: {e}")
                else:
                    st.warning("Please enter the student's full name.")

    # =========================================================================
    # TAB 3: Live Webinars & PragyanAI Outreach Events
    # =========================================================================
    with t_webinars:
        st.subheader("📅 Upcoming PragyanAI Live Masterclasses & Outreach Events")
        st.caption("Join interactive online sessions, view speaker credentials, and access direct Google Meet / Zoom join links.")

        mock_events = [
            {
                "title": "Generative AI & Agentic RAG Foundation for High Schoolers",
                "date": "Saturday, September 5, 2026",
                "time": "11:00 AM - 1:00 PM IST",
                "track": "Generative AI & Prompt Engineering",
                "speaker": "Dr. Sateesh Ambesange",
                "designation": "Founder & CEO, PragyanAI (NITK Alumnus)",
                "platform": "Google Meet",
                "meet_link": "https://meet.google.com/abc-defg-hij",
                "fee": "100% Free (Sponsored Cohort)",
                "audience": "11th & 12th Grade Science & Computer Science Students",
                "description": "An interactive introduction to Large Language Models, prompt crafting, and building simple RAG applications."
            },
            {
                "title": "Semiconductor VLSI & FPGA Prototyping Masterclass",
                "date": "Sunday, September 6, 2026",
                "time": "3:00 PM - 5:00 PM IST",
                "track": "Semiconductor Design",
                "speaker": "Prof. R. M. Kulkarni",
                "designation": "Principal VLSI Architect & Academic Advisor",
                "platform": "Zoom Webinar",
                "meet_link": "https://zoom.us/j/1234567890",
                "fee": "100% Free",
                "audience": "Aspiring ECE & Electronics Engineering Aspirants",
                "description": "Discover how microchips are designed, verified, and manufactured using cutting-edge EDA simulation tools."
            }
        ]

        for ev in mock_events:
            with st.expander(f"📌 {ev['title']} — {ev['date']}", expanded=True):
                c_ev1, c_ev2 = st.columns([2, 1])
                with c_ev1:
                    st.markdown(f"**Track:** {ev['track']}")
                    st.markdown(f"**Lead Speaker:** {ev['speaker']} ({ev['designation']})")
                    st.markdown(f"**Schedule:** {ev['time']}")
                    st.markdown(f"**Target Audience:** {ev['audience']}")
                    st.markdown(f"*{ev['description']}*")
                with c_ev2:
                    st.markdown(f"**Platform:** {ev['platform']}")
                    st.markdown(f"**Fee:** {ev['fee']}")
                    st.link_button(f"🔗 Join via {ev['platform']}", ev['meet_link'], use_container_width=True)

    # =========================================================================
    # TAB 4: Event Media Gallery & Student Feedback Q&A
    # =========================================================================
    with t_gallery:
        st.subheader("📸 PragyanAI Outreach Event Highlights & Photo Gallery")
        st.caption("Glimpses from recent campus bootcamps, lab sessions, and interactive engineering counselling interactions.")

        # Photo Gallery Grid Simulation
        g_col1, g_col2, g_col3 = st.columns(3)
        with g_col1:
            st.image("https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=600&q=80", caption="AI Coding Bootcamp at National Public School")
        with g_col2:
            st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80", caption="Robotics & Hardware Hands-on Session")
        with g_col3:
            st.image("https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80", caption="Student Career Counseling & Option Entry Seminar")

        st.markdown("---")
        st.subheader("💬 Student Questions & College Counseling Q&A Log")
        st.caption("Real queries raised by high school students during recent outreach webinars, answered by PragyanAI mentors.")

        qa_logs = [
            {
                "student": "Aakash M. (12th Grade Science, Bishop Cotton)",
                "question": "What is the difference in core career prospects between Artificial Intelligence & Data Science versus traditional Computer Science Engineering?",
                "answer": "Answered by Dr. Sateesh Ambesange: CSE gives you a broad foundation in operating systems and networks, whereas AI-DS focuses heavily on machine learning algorithms, math, and data pipelines. Both enjoy identical top-tier recruiter access at RVCE and BMSCE."
            },
            {
                "student": "Sneha Rao (PU 2nd Year, National PU College)",
                "question": "How should I plan my option entry for KCET if my rank falls around 4,500?",
                "answer": "Answered by Admissions Desk: At rank 4,500, you have secure access to core branches in Tier-1 autonomous colleges like MSRIT and DSCE, and top emerging branches (AI/Data Science) at RVCE or BMSCE during Round 2."
            },
            {
                "student": "Kiran Kumar (11th Grade, Kendriya Vidyalaya)",
                "question": "Are these PragyanAI coding bootcamps certified for our college portfolios?",
                "answer": "Answered by Program Coordinator: Yes! Every student receives a verifiable digital e-credential certificate with a unique validation hash."
            }
        ]

        for qa in qa_logs:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1rem; margin-bottom:0.75rem;">
                        <p style="margin:0; font-size:0.9rem; color:#1e3a8a;"><b>❓ {qa['student']}</b></p>
                        <p style="margin:0.3rem 0 0.5rem 0; font-size:0.92rem; color:#0f172a;">"{qa['question']}"</p>
                        <p style="margin:0; font-size:0.88rem; color:#059669; background:#f0fdf4; padding:0.5rem; border-radius:6px; border-left:3px solid #10b981;">
                            <b>💡 {qa['answer']}</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    render_school_partner_view()
