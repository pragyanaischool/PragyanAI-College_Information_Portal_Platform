"""
src/ui/views/2_🏫_School_Partner.py

School & PU College Partner Desk: Bulk Student Enrollment, Free AI Bootcamps,
Verifiable E-Certificate Generator, and Live Webinar Schedules.
"""

import streamlit as st
from src.core.database import get_db
from src.db.repository import CollegeRepository
from src.ui.styles import inject_custom_css, render_metric_card
from src.utils.certificate_gen import generate_event_certificate


def render_school_partner_view():
    inject_custom_css()

    st.title("🏫 High School & PU College Outreach Partner Desk")
    st.markdown("Enroll classroom cohorts for free emerging technology masterclasses, book campus discovery visits, and issue verifiable certificates.")

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

    t_reg, t_cert, t_webinars = st.tabs(["📝 Bulk Cohort Enrollment", "🎓 Generate Student E-Certificates", "📅 Upcoming Live Masterclasses"])

    # Tab 1: Bulk School Cohort Registration
    with t_reg:
        st.subheader("Enroll Your Institution Cohort for Free Emerging-Tech Bootcamps")
        with st.form("school_bulk_reg_form"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                school_name = st.text_input("School / Pre-University College Name *")
                city = st.text_input("City / District *")
                coord_name = st.text_input("Coordinator / Principal Name *")
            with col_s2:
                coord_email = st.text_input("Official Email Address *")
                coord_phone = st.text_input("Contact Phone Number *")
                batch_size = st.slider("Expected Participating Student Batch Size:", 25, 500, 100)

            program = st.selectbox(
                "Select Outreach Program Track:",
                [
                    "Free Generative AI & Prompt Engineering 2-Day Bootcamp",
                    "IoT & Robotics Discovery Lab Session",
                    "Engineering Stream Selector & Career Aptitude Test",
                    "KCET & COMEDK Option Entry Strategy Session",
                    "Semiconductor VLSI & FPGA Prototyping Workshop",
                ],
            )
            mou = st.checkbox("Our institution is interested in signing a continuous STEM Outreach MOU.")

            if st.form_submit_button("Confirm Institutional Batch Booking", type="primary"):
                if not school_name or not coord_email or not coord_phone:
                    st.error("Please fill in all mandatory fields.")
                else:
                    with get_db() as db:
                        repo = CollegeRepository(db)
                        repo.register_partner_school({
                            "school_name": school_name,
                            "city": city,
                            "coordinator_name": coord_name,
                            "coordinator_email": coord_email,
                            "coordinator_phone": coord_phone,
                            "registered_batch_size": batch_size,
                            "selected_program": program,
                            "mou_signed": mou,
                        })
                    st.success(f"Batch registered successfully! Confirmation and student join links dispatched to {coord_email}")

    # Tab 2: Certificate Generator
    with t_cert:
        st.subheader("Issue Verifiable E-Certificates for Attended Cohorts")
        with st.form("cert_form"):
            c_name = st.text_input("Student Full Name:")
            c_school = st.text_input("Institution Name:", value="National Public School")
            c_event = st.selectbox(
                "Masterclass Attended:",
                [
                    "Generative AI, RAG & Agentic AI using LangGraph",
                    "Hands-On Robotics, Autonomous Rovers & Micro-Sensors",
                    "Semiconductor VLSI, RTL Design & FPGA Prototyping",
                    "Engineering Stream Selector & Career Aptitude Masterclass",
                ],
            )
            if st.form_submit_button("Generate Official Landscape Certificate (PDF)"):
                if c_name:
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
                    st.success("Certificate compiled and verified successfully!")

    # Tab 3: Webinar Schedule
    with t_webinars:
        st.subheader("Upcoming Technical Outreach Masterclasses")
        with get_db() as db:
            repo = CollegeRepository(db)
            events = repo.get_active_outreach_events()

        for ev in events:
            with st.expander(f"📌 {ev.title} ({ev.event_date})", expanded=True):
                st.markdown(f"**Track:** {ev.track} | **Speaker:** {ev.speaker_name} ({ev.speaker_designation})")
                st.markdown(f"**Time:** {ev.event_time} | **Platform:** {ev.platform} | **Fee:** {ev.registration_fee}")
                st.markdown(f"**Target Audience:** {ev.target_audience}")
                st.markdown(f"**Direct Join URL:** [{ev.platform}]({ev.brochure_asset})")


if __name__ == "__main__":
    render_school_partner_view()
