"""
src/ui/views/16_College_Search_Directory.py

Aspirant College Search & Advanced Filter Directory:
Allows students and parents to filter colleges by State, District, City, and Institution Type.
Provides clear definitions of institutional categories, total intake numbers, and department-wise seat matrices.
"""

import pandas as pd
import streamlit as st
from src.core.database import get_db
from src.db.models import College, Department


def render_college_search_directory_view():
    """Renders the comprehensive college directory with advanced multi-criteria search and intake breakdown."""
    st.title(" Comprehensive College Master Directory & Advanced Search")
    st.markdown(
        "Explore and filter engineering institutions across Karnataka and India. Search by geography, "
        "inspect institutional classifications (University vs. Autonomous vs. Affiliated), and review department-wise seat intakes."
    )
    st.markdown("---")

    # 1. Educational Glossary & Definitions Expander
    with st.expander(" Glossary: What do University, Autonomous, and Affiliated Colleges mean?"):
        st.markdown(
            """
            -  **University (Deemed / State / Private):** 
              Universities have the statutory authority to design their own curricula, conduct examinations, 
              and award degrees directly under their own seal. They often span multiple faculties and research centers.
            -  **Autonomous Colleges:** 
              These institutions are affiliated with a parent university (e.g., VTU) but possess academic freedom. 
              They design their own updated syllabi, conduct internal tests, and grade students independently, 
              allowing for faster curriculum modernization (e.g., introducing AI/GenAI tracks).
            - 🔗 **University Affiliated (Non-Autonomous):** 
              Colleges that strictly follow the rigid curriculum, exam schedules, and evaluation guidelines 
              prescribed by the central affiliating university (e.g., Visvesvaraya Technological University - VTU).
            """
        )

    # Fetch colleges from DB
    try:
        with get_db() as db:
            colleges = db.query(College).all()
    except Exception:
        colleges = []

    # Fallback demo data if DB is empty
    if not colleges:
        class DemoCol:
            def __init__(self, code, name, state, district, city, aut, intake, median, highest, website):
                self.code = code
                self.name = name
                self.state = state
                self.district = district
                self.city = city
                self.autonomous = aut
                self.intake_total = intake
                self.median_ctc_lpa = median
                self.highest_ctc_lpa = highest
                self.website_link = website
        colleges = [
            DemoCol("RVCE", "RV College of Engineering", "Karnataka", "Bengaluru Urban", "Bengaluru", True, 1200, 14.5, 55.0, "https://rvce.edu.in"),
            DemoCol("BMSCE", "BMS College of Engineering", "Karnataka", "Bengaluru Urban", "Bengaluru", True, 1400, 11.2, 48.0, "https://bmsce.ac.in"),
            DemoCol("MSRIT", "MS Ramaiah Institute of Technology", "Karnataka", "Bengaluru Urban", "Bengaluru", True, 1350, 12.0, 50.0, "https://msrit.edu"),
            DemoCol("SJCE", "Sri Jayachamarajendra College of Engineering", "Karnataka", "Mysuru", "Mysuru", True, 900, 9.5, 42.0, "https://sjce.ac.in"),
        ]

    # 2. Advanced Multi-Criteria Filter Controls
    st.markdown("###  Filter & Search Controls")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        states = ["All States"] + sorted(list(set(c.state for c in colleges if c.state)))
        sel_state = st.selectbox("Filter by State:", states)

    with f_col2:
        districts = ["All Districts"] + sorted(list(set(c.district for c in colleges if c.district)))
        sel_district = st.selectbox("Filter by District:", districts)

    with f_col3:
        cities = ["All Cities"] + sorted(list(set(c.city for c in colleges if c.city)))
        sel_city = st.selectbox("Filter by City:", cities)

    with f_col4:
        col_types = ["All Types", "Autonomous", "University Affiliated / Non-Autonomous", "University"]
        sel_type = st.selectbox("Institution Classification:", col_types)

    # Apply Filters
    filtered_colleges = colleges
    if sel_state != "All States":
        filtered_colleges = [c for c in filtered_colleges if c.state == sel_state]
    if sel_district != "All Districts":
        filtered_colleges = [c for c in filtered_colleges if c.district == sel_district]
    if sel_city != "All Cities":
        filtered_colleges = [c for c in filtered_colleges if c.city == sel_city]
    if sel_type == "Autonomous":
        filtered_colleges = [c for c in filtered_colleges if getattr(c, 'autonomous', True)]
    elif sel_type == "University Affiliated / Non-Autonomous":
        filtered_colleges = [c for c in filtered_colleges if not getattr(c, 'autonomous', True)]

    st.markdown(f"**Showing `{len(filtered_colleges)}` matching institutions**")
    st.markdown("---")

    # 3. College Cards & Department Intake Breakdown
    for col in filtered_colleges:
        with st.container():
            col_info, col_metrics = st.columns([3, 2])
            with col_info:
                st.markdown(f"###  {col.name} (`{col.code}`)")
                st.caption(f" **Location:** {col.city}, {col.district}, {col.state} | **Classification:** {'Autonomous' if getattr(col, 'autonomous', True) else 'Affiliated'}")
                st.write(f" **Median CTC:** ₹ {getattr(col, 'median_ctc_lpa', 10.0)} LPA | 🚀 **Peak Offer:** ₹ {getattr(col, 'highest_ctc_lpa', 40.0)} LPA")
            with col_metrics:
                st.metric("Total Annual Intake", f"{getattr(col, 'intake_total', 1000)} Seats")

            # Fetch department intake breakdown from DB
            try:
                with get_db() as db:
                    depts = db.query(Department).filter_by(college_code=col.code).all()
            except Exception:
                depts = []

            if depts:
                dept_df = pd.DataFrame([
                    {"Branch Code": d.branch_code, "Branch Name": d.branch_name, "Intake Seats": d.intake, "NBA Status": d.nba_status}
                    for d in depts
                ])
                st.markdown("#####  Department-Wise Seat Intake Matrix:")
                st.dataframe(dept_df, use_container_width=True, hide_index=True)
            else:
                st.info(f"Department seat distribution matrix available upon publishing for {col.name}.")

            st.markdown("---")


if __name__ == "__main__":
    render_college_search_directory_view()
