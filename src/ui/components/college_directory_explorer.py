"""
src/ui/components/college_directory_explorer.py

State-wise, District-wise, and City-wise College Directory Explorer:
- Cascading Multi-Level Geo Filters (State -> District -> City)
- Free-text Name, CET Code, and Branch Filter
- Comprehensive Metadata: CET Code, Departments, Intakes, Address, Website & Fees
- In-Detail College Card Modal
"""

from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.db.repository import CollegeRepository


def render_college_directory_explorer():
    """Renders the comprehensive Geographic & Institutional College Explorer."""
    st.subheader("🗺️ Comprehensive College Directory Explorer")
    st.caption("Search across State, District, City, CET Codes, Branch Intakes, Physical Addresses, and Direct Web Portals.")

    # 1. Fetch raw data safely inside session
    with get_db() as db:
        repo = CollegeRepository(db)
        raw_colleges = repo.get_all_colleges()

    colleges: List[Dict[str, Any]] = []
    for c in raw_colleges:
        if isinstance(c, dict):
            colleges.append(dict(c))
        else:
            colleges.append({
                "code": str(getattr(c, "code", "")),
                "name": str(getattr(c, "name", "")),
                "short_name": str(getattr(c, "short_name", "")),
                "state": str(getattr(c, "state", "Karnataka")),
                "district": str(getattr(c, "district", "Bengaluru Urban")),
                "city": str(getattr(c, "city", "Bengaluru")),
                "address": str(getattr(c, "address", "Bengaluru, Karnataka")),
                "established_year": getattr(c, "established_year", 1960),
                "autonomous": getattr(c, "autonomous", True),
                "naac_grade": str(getattr(c, "naac_grade", "A")),
                "naac_cgpa": getattr(c, "naac_cgpa", 3.0),
                "nirf_rank_2025": getattr(c, "nirf_rank_2025", 100),
                "intake_total": getattr(c, "intake_total", 1200),
                "govt_fee_cet_lakhs": getattr(c, "govt_fee_cet_lakhs", 1.07),
                "comedk_fee_lakhs": getattr(c, "comedk_fee_lakhs", 2.81),
                "mgmt_fee_cse_lakhs": getattr(c, "mgmt_fee_cse_lakhs", 10.0),
                "median_ctc_lpa": getattr(c, "median_ctc_lpa", 8.0),
                "highest_ctc_lpa": getattr(c, "highest_ctc_lpa", 30.0),
                "website_link": getattr(c, "website_link", "https://cetonline.karnataka.gov.in/kea/"),
                "departments_and_intake": getattr(c, "departments_and_intake", {
                    "Computer Science & Engg": 240,
                    "AI & Data Science": 120,
                    "Electronics & Communication": 180,
                    "Mechanical Engineering": 120,
                }),
            })

    if not colleges:
        st.info("No colleges found in the database. Run seed initialization.")
        return

    # 2. Cascading Geographical Filters
    all_states = sorted(list({c.get("state", "Karnataka") for c in colleges}))
    
    col_g1, col_g2, col_g3, col_g4 = st.columns([1, 1.2, 1.2, 1.5])

    with col_g1:
        sel_state = st.selectbox("1. State:", ["All States"] + all_states, index=0)

    # Filter available districts based on state
    districts_filtered = sorted(list({
        c.get("district", "Bengaluru Urban")
        for c in colleges
        if sel_state == "All States" or c.get("state") == sel_state
    }))

    with col_g2:
        sel_district = st.selectbox("2. District:", ["All Districts"] + districts_filtered, index=0)

    # Filter available cities based on district
    cities_filtered = sorted(list({
        c.get("city", "Bengaluru")
        for c in colleges
        if (sel_state == "All States" or c.get("state") == sel_state) and
           (sel_district == "All Districts" or c.get("district") == sel_district)
    }))

    with col_g3:
        sel_city = st.selectbox("3. City / Town:", ["All Cities"] + cities_filtered, index=0)

    with col_g4:
        search_query = st.text_input(
            "4. Search Name / CET Code / Branch:",
            placeholder="e.g. RVCE, E001, AI-DS, Mysuru",
        )

    # 3. Apply Multi-Parameter Filtering Logic
    filtered = []
    for c in colleges:
        match_state = (sel_state == "All States") or (c.get("state") == sel_state)
        match_district = (sel_district == "All Districts") or (c.get("district") == sel_district)
        match_city = (sel_city == "All Cities") or (c.get("city") == sel_city)

        match_text = True
        if search_query.strip():
            q = search_query.strip().lower()
            dept_keys = " ".join(c.get("departments_and_intake", {}).keys()).lower()
            match_text = (
                q in c.get("name", "").lower() or
                q in c.get("short_name", "").lower() or
                q in c.get("code", "").lower() or
                q in c.get("city", "").lower() or
                q in dept_keys
            )

        if match_state and match_district and match_city and match_text:
            filtered.append(c)

    # 4. Display Results Summary & Interactive Table
    st.markdown(f"**Found {len(filtered)} Colleges matching criteria:**")

    if not filtered:
        st.warning("No colleges match the selected geographical or search filters. Try widening your criteria.")
        return

    table_data = []
    for c in filtered:
        # Format department breakdown string
        depts_dict = c.get("departments_and_intake", {})
        depts_summary = ", ".join([f"{k} ({v})" for k, v in list(depts_dict.items())[:3]])
        if len(depts_dict) > 3:
            depts_summary += f", +{len(depts_dict)-3} more"

        table_data.append({
            "CET Code": c.get("code"),
            "College Name": f"{c.get('name')} ({c.get('short_name')})",
            "District": c.get("district"),
            "City": c.get("city"),
            "Total Intake": f"{c.get('intake_total'):,} Seats",
            "NIRF 2025": f"#{c.get('nirf_rank_2025')}",
            "NAAC": f"{c.get('naac_grade')} ({c.get('naac_cgpa')})",
            "Govt Fee": f"₹{c.get('govt_fee_cet_lakhs')}L/yr",
            "Median CTC": f"₹{c.get('median_ctc_lpa')} LPA",
            "Key Departments & Intake": depts_summary,
            "Official Website": c.get("website_link"),
        })

    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # 5. Deep-Dive Explorer Cards for Selected College
    st.markdown("---")
    st.markdown("### 🔍 Deep-Dive Institutional Breakdown")
    
    col_cards = st.selectbox(
        "Select a college from filtered results to view complete departments, full address & portal links:",
        [f"{c['code']} - {c['name']} ({c['city']})" for c in filtered],
        index=0,
        key="directory_card_selector",
    )

    selected_card_code = col_cards.split(" - ")[0]
    target_c = next((c for c in filtered if c["code"] == selected_card_code), filtered[0])

    # Render Institutional Deep Dive Card
    st.markdown(
        f"""
        <div style="
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-left: 5px solid #2563eb;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            margin-top: 0.5rem;
        ">
            <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
                <div>
                    <h3 style="margin:0; color:#0f172a; font-size:1.3rem;">{target_c['name']} ({target_c['short_name']})</h3>
                    <p style="margin:0.25rem 0 0 0; color:#64748b; font-size:0.88rem;">
                        📍 <b>Full Address:</b> {target_c['address']}
                    </p>
                    <p style="margin:0.25rem 0 0 0; color:#475569; font-size:0.85rem;">
                        🏛️ <b>CET / COMEDK Code:</b> <span style="color:#2563eb; font-weight:700;">{target_c['code']}</span> | 
                        State: <b>{target_c['state']}</b> | District: <b>{target_c['district']}</b> | City: <b>{target_c['city']}</b> | Estd: <b>{target_c['established_year']}</b>
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Breakdown Grid: Departments & Intakes vs Financials & Links
    cd_col1, cd_col2 = st.columns([1.3, 1])

    with cd_col1:
        st.markdown("#### 📚 Department-Wise Seat Allocation (2026)")
        depts_full = target_c.get("departments_and_intake", {})
        df_depts = pd.DataFrame([
            {"Department / Specialization": dept, "Sanctioned Intake": f"{seats} Seats"}
            for dept, seats in depts_full.items()
        ])
        st.dataframe(df_depts, use_container_width=True, hide_index=True)

    with cd_col2:
        st.markdown("#### 🌐 Portals & Key Performance Indicators")
        st.link_button("🏛️ Visit Official College Website", target_c.get("website_link"), use_container_width=True)
        st.link_button("📑 KEA Seat Matrix Portal", "https://cetonline.karnataka.gov.in/kea/", use_container_width=True)

        st.metric("Total Sanctioned Intake", f"{target_c['intake_total']:,} Seats")
        st.metric("Median CTC vs Highest CTC", f"₹{target_c['median_ctc_lpa']} LPA", delta=f"Highest: ₹{target_c['highest_ctc_lpa']} LPA")
        st.metric("Government CET Annual Fee", f"₹{target_c['govt_fee_cet_lakhs']} Lakhs / yr")
