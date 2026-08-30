"""
src/ui/views/17_Admin_College_Editor.py

Admin College Information Management & Master Data Entry Portal:
Allows administrators to add new engineering colleges, update intake quotas, 
modify fee structures (CET, COMEDK, Management), and adjust median CTC packages 
directly within the PragyanAI central database.
"""

import streamlit as st
from src.core.database import get_db
from src.db.models import College


def render_admin_college_editor_view():
    """Renders the admin panel for adding and modifying complete college master records."""
    st.title(" Admin Portal: College Master Data Management")
    st.markdown(
        "Administrators can add new engineering colleges, update intake capacities, "
        "modify fee structures (CET, COMEDK, Management), and adjust median CTC packages."
    )
    st.markdown("---")

    with st.form("admin_college_add_form"):
        st.markdown("###  Add / Update College Master Record")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            code = st.text_input("College Code (Unique) *", placeholder="e.g. PESU")
            name = st.text_input("Full Institution Name *", placeholder="e.g. PES University")
            short_name = st.text_input("Short Name", placeholder="PESU")
            state = st.text_input("State", value="Karnataka")
        with c2:
            district = st.text_input("District", value="Bengaluru Urban")
            city = st.text_input("City *", placeholder="Bengaluru")
            established = st.number_input("Established Year", min_value=1900, max_value=2026, value=1988)
            autonomous = st.checkbox("Is Autonomous?", value=True)
        with c3:
            intake_total = st.number_input("Total Intake Seats", min_value=100, max_value=5000, value=1200)
            median_ctc = st.number_input("Median CTC (LPA)", min_value=2.0, max_value=60.0, value=14.0)
            highest_ctc = st.number_input("Highest CTC (LPA)", min_value=5.0, max_value=120.0, value=50.0)
            nirf = st.number_input("NIRF Rank", min_value=1, max_value=500, value=45)

        st.markdown("---")
        st.markdown("####  Fee Structures & Governance")
        f1, f2, f3 = st.columns(3)
        with f1:
            govt_fee = st.number_input("Govt CET Fee (Lakhs/Yr)", value=1.0)
        with f2:
            comedk_fee = st.number_input("COMEDK Fee (Lakhs/Yr)", value=2.6)
        with f3:
            mgmt_fee = st.number_input("Management Fee (Lakhs/Yr)", value=6.5)

        vision = st.text_area("Institutional Vision", value="Excellence in technical education and research.")
        website = st.text_input("Official Website URL", placeholder="https://college.edu")

        if st.form_submit_button(" Save / Upsert College Record in Database", type="primary"):
            if not code or not name or not city:
                st.error("Please fill in all mandatory fields (College Code, Name, City).")
            else:
                try:
                    with get_db() as db:
                        college = db.query(College).filter_by(code=code).first()
                        if college:
                            college.name = name
                            college.short_name = short_name or code
                            college.state = state
                            college.district = district
                            college.city = city
                            college.established_year = established
                            college.autonomous = autonomous
                            college.intake_total = intake_total
                            college.median_ctc_lpa = median_ctc
                            college.highest_ctc_lpa = highest_ctc
                            college.nirf_rank_2025 = nirf
                            college.govt_fee_cet_lakhs = govt_fee
                            college.comedk_fee_lakhs = comedk_fee
                            college.mgmt_fee_cse_lakhs = mgmt_fee
                            college.vision = vision
                            college.website_link = website
                        else:
                            college = College(
                                code=code,
                                name=name,
                                short_name=short_name or code,
                                state=state,
                                district=district,
                                city=city,
                                established_year=established,
                                autonomous=autonomous,
                                intake_total=intake_total,
                                median_ctc_lpa=median_ctc,
                                highest_ctc_lpa=highest_ctc,
                                nirf_rank_2025=nirf,
                                govt_fee_cet_lakhs=govt_fee,
                                comedk_fee_lakhs=comedk_fee,
                                mgmt_fee_cse_lakhs=mgmt_fee,
                                vision=vision,
                                website_link=website
                            )
                            db.add(college)
                        db.commit()
                    st.success(f"✅ Successfully saved master record for **{name} (`{code}`)** in the central database!")
                except Exception as e:
                    st.error(f"Error saving college record: {e}")


if __name__ == "__main__":
    render_admin_college_editor_view()
