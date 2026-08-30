"""
src/ui/components/college_directory_explorer.py

Comprehensive College Directory Explorer component for the Aspirant Desk.
Allows filtering across State, District, City/Town, CET Codes, Branch Intakes,
Physical Addresses, and Direct Web Portals with safe null-guards.
"""

from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.db.models import College


def _fetch_all_colleges_safely() -> List[Dict[str, Any]]:
    """Fetches all colleges as standalone dictionaries with robust null-guards."""
    with get_db() as db:
        colleges = db.query(College).order_by(College.nirf_rank_2025.asc()).all()
        result = []
        for c in colleges:
            name_val = str(getattr(c, "name", "") or "")
            auto_val = bool(getattr(c, "autonomous", True))

            if "PES" in name_val:
                affil = "Private State University"
            elif auto_val:
                affil = "Autonomous (VTU Affiliated)"
            else:
                affil = "VTU Affiliated (Non-Autonomous)"

            depts_raw = getattr(c, "departments_and_intake", None)
            depts_dict = dict(depts_raw) if isinstance(depts_raw, dict) else {}

            recruiters_raw = getattr(c, "top_recruiters", None)
            recruiters_list = list(recruiters_raw) if isinstance(recruiters_raw, list) else []

            coas_raw = getattr(c, "coas_and_centers_of_excellence", None)
            coas_list = list(coas_raw) if isinstance(coas_raw, list) else []

            result.append({
                "id": str(getattr(c, "id", "") or ""),
                "code": str(getattr(c, "code", "") or ""),
                "name": name_val,
                "short_name": str(getattr(c, "short_name", "") or ""),
                "state": str(getattr(c, "state", "Karnataka") or "Karnataka"),
                "district": str(getattr(c, "district", "Bengaluru Urban") or "Bengaluru Urban"),
                "city": str(getattr(c, "city", "Bengaluru") or "Bengaluru"),
                "address": str(getattr(c, "address", "Bengaluru, Karnataka") or "Bengaluru, Karnataka"),
                "established_year": int(getattr(c, "established_year", 1960) or 1960),
                "autonomous": auto_val,
                "affiliation_type": affil,
                "naac_grade": str(getattr(c, "naac_grade", "A") or "A"),
                "naac_cgpa": float(getattr(c, "naac_cgpa", 3.0) or 3.0),
                "nba_accredited_programs": int(getattr(c, "nba_accredited_programs", 0) or 0),
                "nirf_rank_2025": int(getattr(c, "nirf_rank_2025", 100) or 100),
                "intake_total": int(getattr(c, "intake_total", 1200) or 1200),
                "mgmt_fee_cse_lakhs": float(getattr(c, "mgmt_fee_cse_lakhs", 10.0) or 10.0),
                "govt_fee_cet_lakhs": float(getattr(c, "govt_fee_cet_lakhs", 1.07) or 1.07),
                "comedk_fee_lakhs": float(getattr(c, "comedk_fee_lakhs", 2.81) or 2.81),
                "median_ctc_lpa": float(getattr(c, "median_ctc_lpa", 8.0) or 8.0),
                "highest_ctc_lpa": float(getattr(c, "highest_ctc_lpa", 25.0) or 25.0),
                "departments_and_intake": depts_dict,
                "top_recruiters": recruiters_list,
                "coas_and_centers_of_excellence": coas_list,
                "website_link": str(getattr(c, "website_link", "") or "https://cetonline.karnataka.gov.in/kea/"),
                "video_tour_url": str(getattr(c, "video_tour_url", "") or "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
                "principal_statement": str(getattr(c, "principal_statement", "") or ""),
            })
        return result


def render_college_directory_explorer():
    """Renders the state, district, city, CET code, and branch intake directory explorer."""
    st.subheader("🗺️ Comprehensive College Directory Explorer")
    st.caption("Search across State, District, City, CET Codes, Branch Intakes, Physical Addresses, and Direct Web Portals.")

    colleges = _fetch_all_colleges_safely()

    # Extract unique filter options safely
    states = sorted(list({c["state"] for c in colleges}))
    districts = sorted(list({c["district"] for c in colleges}))
    cities = sorted(list({c["city"] for c in colleges}))

    # Filter Controls UI
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    with f_c1:
        sel_state = st.selectbox("1. State:", ["All States"] + states, index=0)
    with f_c2:
        sel_district = st.selectbox("2. District:", ["All Districts"] + districts, index=0)
    with f_c3:
        sel_city = st.selectbox("3. City / Town:", ["All Cities"] + cities, index=0)
    with f_c4:
        search_query = st.text_input("4. Search Name / CET Code / Branch:", placeholder="e.g. RVCE, E001, CSE")

    # Apply filters
    filtered_colleges = []
    for c in colleges:
        if sel_state != "All States" and c["state"] != sel_state:
            continue
        if sel_district != "All Districts" and c["district"] != sel_district:
            continue
        if sel_city != "All Cities" and c["city"] != sel_city:
            continue

        if search_query and search_query.strip():
            q = search_query.strip().lower()
            name_match = q in c["name"].lower() or q in c["short_name"].lower()
            code_match = q in c["code"].lower()
            city_match = q in c["city"].lower()
            
            # Safe check on departments keys
            branch_match = any(q in b_code.lower() for b_code in c["departments_and_intake"].keys())

            if not (name_match or code_match or city_match or branch_match):
                continue

        filtered_colleges.append(c)

    st.markdown(f"**Found {len(filtered_colleges)} Colleges matching criteria:**")
    st.markdown("<br/>", unsafe_allow_html=True)

    if not filtered_colleges:
        st.warning("No institutions matched your filter criteria. Try resetting the filters.")
        return

    for c in filtered_colleges:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 1.25rem;
                    margin-bottom: 1rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="background: #eff6ff; color: #2563eb; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 700; font-size: 0.8rem;">
                                CET Code: {c['code']}
                            </span>
                            <h3 style="margin: 0.4rem 0 0.2rem 0; color: #0f172a; font-size: 1.25rem;">
                                {c['name']} ({c['short_name']})
                            </h3>
                            <p style="color: #64748b; font-size: 0.88rem; margin: 0;">
                                📍 <b>Address:</b> {c['address']} | <b>District:</b> {c['district']}, {c['state']} | <b>Est:</b> {c['established_year']}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: #059669; font-weight: 700; font-size: 0.9rem;">NIRF #{c['nirf_rank_2025']}</span><br/>
                            <span style="color: #64748b; font-size: 0.8rem;">NAAC {c['naac_grade']} (CGPA {c['naac_cgpa']})</span>
                        </div>
                    </div>
                    <hr style="margin: 0.75rem 0; border: none; border-top: 1px solid #f1f5f9;"/>
                    <div style="display: flex; gap: 2rem; font-size: 0.85rem; color: #334155;">
                        <div><b>Governance:</b> {c['affiliation_type']}</div>
                        <div><b>Total Intake:</b> {c['intake_total']} seats</div>
                        <div><b>Median CTC:</b> ₹{c['median_ctc_lpa']} LPA (Highest: ₹{c['highest_ctc_lpa']} LPA)</div>
                        <div><b>Govt Fee:</b> ₹{c['govt_fee_cet_lakhs']}L/yr</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Expandable department intake breakdown
            depts = c["departments_and_intake"]
            if depts:
                with st.expander(f"📂 View Branch-wise Approved Intake Map ({len(depts)} Departments)", expanded=False):
                    d_cols = st.columns(3)
                    for d_idx, (b_name, b_seats) in enumerate(depts.items()):
                        with d_cols[d_idx % 3]:
                            st.markdown(f"• **{b_name}**: `{b_seats} Seats`")

            st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
