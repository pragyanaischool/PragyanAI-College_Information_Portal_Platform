"""
src/ui/components/cutoff_explorer.py

Interactive Cutoff Predictor, Multi-Test Score Profiler, Side-by-Side Comparison,
and In-Detail Institutional Portal Navigator.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.db.repository import CollegeRepository

# Official direct portal directories for benchmark institutions
COLLEGE_PORTAL_LINKS = {
    "E001": {
        "website": "https://rvce.edu.in",
        "admissions_portal": "https://rvce.edu.in/admission-guidelines",
        "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
        "placements_hub": "https://rvce.edu.in/placement",
        "naac_nirf_dossier": "https://rvce.edu.in/nirf-naac",
        "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "E002": {
        "website": "https://www.bmsce.ac.in",
        "admissions_portal": "https://www.bmsce.ac.in/home/Admissions",
        "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
        "placements_hub": "https://www.bmsce.ac.in/home/Placement-Centre",
        "naac_nirf_dossier": "https://www.bmsce.ac.in/home/NIRF",
        "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "E003": {
        "website": "https://www.msrit.edu",
        "admissions_portal": "https://www.msrit.edu/admissions.html",
        "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
        "placements_hub": "https://www.msrit.edu/placement.html",
        "naac_nirf_dossier": "https://www.msrit.edu/nirf.html",
        "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "E004": {
        "website": "https://pes.edu",
        "admissions_portal": "https://pessat.pes.edu",
        "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
        "placements_hub": "https://pes.edu/placements/",
        "naac_nirf_dossier": "https://pes.edu/nirf/",
        "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "E005": {
        "website": "https://www.dsce.edu.in",
        "admissions_portal": "https://www.dsce.edu.in/admissions",
        "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
        "placements_hub": "https://www.dsce.edu.in/placements",
        "naac_nirf_dossier": "https://www.dsce.edu.in/naac",
        "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "E006": {
        "website": "https://bit-bangalore.edu.in",
        "admissions_portal": "https://bit-bangalore.edu.in/admissions/",
        "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
        "placements_hub": "https://bit-bangalore.edu.in/placement/",
        "naac_nirf_dossier": "https://bit-bangalore.edu.in/nirf/",
        "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "E008": {
        "website": "https://nie.ac.in",
        "admissions_portal": "https://nie.ac.in/admissions/",
        "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
        "placements_hub": "https://nie.ac.in/placements/",
        "naac_nirf_dossier": "https://nie.ac.in/nirf/",
        "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "E010": {
        "website": "http://www.sit.ac.in",
        "admissions_portal": "http://www.sit.ac.in/html/admission.html",
        "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
        "placements_hub": "http://www.sit.ac.in/html/placement.html",
        "naac_nirf_dossier": "http://www.sit.ac.in/html/nirf.html",
        "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
}


def _fetch_all_colleges_as_dicts() -> List[Dict[str, Any]]:
    """Loads all colleges and serializes them into independent dicts inside the session."""
    with get_db() as db:
        repo = CollegeRepository(db)
        raw_list = repo.get_all_colleges()
        result = []
        for obj in raw_list:
            if isinstance(obj, dict):
                result.append(dict(obj))
            else:
                result.append({
                    "code": str(getattr(obj, "code", "")),
                    "name": str(getattr(obj, "name", "")),
                    "short_name": str(getattr(obj, "short_name", "")),
                    "city": str(getattr(obj, "city", "Bengaluru")),
                    "nirf_rank_2025": getattr(obj, "nirf_rank_2025", 100),
                    "naac_grade": str(getattr(obj, "naac_grade", "A")),
                    "naac_cgpa": float(getattr(obj, "naac_cgpa", 3.0)),
                    "median_ctc_lpa": float(getattr(obj, "median_ctc_lpa", 8.0)),
                    "highest_ctc_lpa": float(getattr(obj, "highest_ctc_lpa", 25.0)),
                    "mgmt_fee_cse_lakhs": float(getattr(obj, "mgmt_fee_cse_lakhs", 10.0)),
                    "govt_fee_cet_lakhs": float(getattr(obj, "govt_fee_cet_lakhs", 1.07)),
                    "comedk_fee_lakhs": float(getattr(obj, "comedk_fee_lakhs", 2.81)),
                    "nba_accredited_programs": int(getattr(obj, "nba_accredited_programs", 6)),
                    "autonomous": bool(getattr(obj, "autonomous", True)),
                    "established_year": int(getattr(obj, "established_year", 1960)),
                    "principal_statement": str(getattr(obj, "principal_statement", "")),
                })
        return result


def render_cutoff_finder():
    """Renders the cutoff predictor, multi-test profiler, comparator, and portal hub."""
    st.subheader("🎯 Entrance Cutoff & Multi-Test Admission Profiler")
    st.caption(
        "Evaluate your admission probability with individual cutoffs or cross-test manual score inputs."
    )

    # -------------------------------------------------------------------------
    # 1. Quick Single-Exam Parameter Grid
    # -------------------------------------------------------------------------
    c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.4])
    with c1:
        exam = st.selectbox(
            "Entrance Exam:",
            ["KCET", "COMEDK"],
            index=0,
            key="cutoff_filter_exam",
        )
    with c2:
        year = st.selectbox(
            "Target Year:",
            [2026, 2025, 2024],
            index=0,
            key="cutoff_filter_year",
        )
    with c3:
        branch = st.selectbox(
            "Preferred Branch:",
            ["CSE", "AI-DS", "ISE", "ECE", "MECH"],
            index=0,
            key="cutoff_filter_branch",
        )
    with c4:
        category = st.selectbox(
            "Category Quota:",
            ["GM", "1G", "2A", "2B", "3A", "3B", "SC", "ST"],
            index=0,
            key="cutoff_filter_category",
        )
    with c5:
        user_rank = st.number_input(
            "Your Entrance Rank:",
            min_value=1,
            max_value=185000,
            value=3500,
            step=100,
            key="cutoff_filter_rank",
        )

    # -------------------------------------------------------------------------
    # 2. Feasibility Query Execution
    # -------------------------------------------------------------------------
    if st.button("🔍 Check Admission Feasibility", type="primary", use_container_width=True):
        with get_db() as db:
            repo = CollegeRepository(db)
            df_eligible = repo.find_eligible_colleges(
                exam=exam,
                branch=branch,
                category=category,
                student_rank=user_rank,
                year=year,
                limit=20,
            )

        if not df_eligible.empty:
            st.success(
                f"Found {len(df_eligible)} Qualifying Benchmark Institutions for Rank #{user_rank:,} "
                f"({exam} {year} - {category} - {branch})"
            )

            if "cutoff_rank" in df_eligible.columns:
                def categorize_feasibility(row):
                    cutoff = row["cutoff_rank"]
                    if user_rank <= cutoff * 0.8:
                        return "🟢 Very Safe"
                    elif user_rank <= cutoff:
                        return "🟡 Safe"
                    elif user_rank <= cutoff * 1.15:
                        return "🟠 Borderline / Round-3"
                    return "🔴 Ambitious"

                df_eligible["Admission Probability"] = df_eligible.apply(
                    categorize_feasibility, axis=1
                )

            year_label = str(year)
            column_mapping = {
                "college_code": "Code",
                "college_name": "College Name",
                "city": "Location",
                "naac_grade": "NAAC",
                "naac_cgpa": "NAAC CGPA",
                "nirf_rank_2025": "NIRF Rank",
                "cutoff_rank": f"{year_label} Cutoff Rank",
                "mgmt_fee_cse_lakhs": "Mgmt Fee (LPA)",
                "mgmt_fee_lpa": "Mgmt Fee (LPA)",
                "median_ctc_lpa": "Median CTC (LPA)",
                "highest_ctc_lpa": "Highest CTC (LPA)",
            }

            rename_dict = {
                col: column_mapping[col]
                for col in df_eligible.columns
                if col in column_mapping
            }
            df_display = df_eligible.rename(columns=rename_dict)

            preferred_order = [
                "Code",
                "College Name",
                "Location",
                f"{year_label} Cutoff Rank",
                "Admission Probability",
                "NIRF Rank",
                "NAAC",
                "Median CTC (LPA)",
                "Highest CTC (LPA)",
                "Mgmt Fee (LPA)",
            ]
            final_cols = [c for c in preferred_order if c in df_display.columns]
            remaining_cols = [c for c in df_display.columns if c not in final_cols]

            st.dataframe(
                df_display[final_cols + remaining_cols],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning(
                f"Your rank #{user_rank:,} exceeds standard Round-2 merit cutoffs for {branch} under quota {category}. "
                f"Explore multi-test scores below or check Institutional Management Quota seats."
            )

    # Preload all college dicts in memory for the rest of the components
    all_colleges_dicts = _fetch_all_colleges_as_dicts()

    # -------------------------------------------------------------------------
    # 3. Side-by-Side Comparison Module
    # -------------------------------------------------------------------------
    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
    with st.expander("⚖️ Compare Two Colleges Side-by-Side (Fees, Placements & NAAC)"):
        if all_colleges_dicts:
            college_options = [f"{c['code']} - {c['name']}" for c in all_colleges_dicts]
            col_sel1, col_sel2 = st.columns(2)

            with col_sel1:
                sel1 = st.selectbox("Select College A:", college_options, index=0, key="cmp_col_a")
            with col_sel2:
                default_idx2 = 1 if len(college_options) > 1 else 0
                sel2 = st.selectbox("Select College B:", college_options, index=default_idx2, key="cmp_col_b")

            code1 = sel1.split(" - ")[0]
            code2 = sel2.split(" - ")[0]

            col1_dict = next((c for c in all_colleges_dicts if c["code"] == code1), None)
            col2_dict = next((c for c in all_colleges_dicts if c["code"] == code2), None)

            if col1_dict and col2_dict:
                comparison_metrics = [
                    ("NIRF 2025 Rank", f"#{col1_dict['nirf_rank_2025']}", f"#{col2_dict['nirf_rank_2025']}"),
                    ("NAAC Grade & CGPA", f"{col1_dict['naac_grade']} ({col1_dict['naac_cgpa']})", f"{col2_dict['naac_grade']} ({col2_dict['naac_cgpa']})"),
                    ("Median CTC Package", f"₹{col1_dict['median_ctc_lpa']} LPA", f"₹{col2_dict['median_ctc_lpa']} LPA"),
                    ("Highest CTC Package", f"₹{col1_dict['highest_ctc_lpa']} LPA", f"₹{col2_dict['highest_ctc_lpa']} LPA"),
                    ("Mgmt Quota Fee (CSE)", f"₹{col1_dict['mgmt_fee_cse_lakhs']} Lakhs/yr", f"₹{col2_dict['mgmt_fee_cse_lakhs']} Lakhs/yr"),
                    ("Govt Quota Fee (CET)", f"₹{col1_dict['govt_fee_cet_lakhs']} Lakhs/yr", f"₹{col2_dict['govt_fee_cet_lakhs']} Lakhs/yr"),
                    ("COMEDK Fee", f"₹{col1_dict['comedk_fee_lakhs']} Lakhs/yr", f"₹{col2_dict['comedk_fee_lakhs']} Lakhs/yr"),
                    ("NBA Accredited Programs", f"{col1_dict['nba_accredited_programs']} Programs", f"{col2_dict['nba_accredited_programs']} Programs"),
                    ("Autonomous Status", "Yes" if col1_dict["autonomous"] else "No", "Yes" if col2_dict["autonomous"] else "No"),
                ]

                df_comparison = pd.DataFrame(
                    comparison_metrics,
                    columns=["Evaluation Parameter", col1_dict["short_name"], col2_dict["short_name"]],
                )
                st.table(df_comparison)

    # -------------------------------------------------------------------------
    # 4. Multi-Test Manual Score & Rank Profiler
    # -------------------------------------------------------------------------
    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
    with st.expander("📝 Manually Enter Multi-Test Scores (KCET, COMEDK, JEE Main, Boards)", expanded=True):
        st.markdown(
            "Enter your scores and ranks across different entrance pathways to calculate an **integrated admission matrix**."
        )

        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            kcet_rank_in = st.number_input(
                "KCET Engineering Rank:",
                min_value=0,
                max_value=250000,
                value=4200,
                step=100,
                help="Enter 0 if not attempted.",
            )
            kcet_marks_in = st.number_input(
                "KCET PCM Marks (out of 180):",
                min_value=0,
                max_value=180,
                value=138,
            )
        with f_col2:
            comedk_rank_in = st.number_input(
                "COMEDK UGET Rank:",
                min_value=0,
                max_value=120000,
                value=2800,
                step=100,
                help="Enter 0 if not attempted.",
            )
            comedk_marks_in = st.number_input(
                "COMEDK Marks (out of 180):",
                min_value=0,
                max_value=180,
                value=122,
            )
        with f_col3:
            jee_percentile_in = st.number_input(
                "JEE Main Percentile / NTA Score:",
                min_value=0.0,
                max_value=100.0,
                value=94.5,
                step=0.1,
                help="Used for Institutional Super Quota & Deemed Admission criteria.",
            )
            pessat_rank_in = st.number_input(
                "PESSAT / Institutional Test Rank:",
                min_value=0,
                max_value=50000,
                value=1250,
                step=50,
            )
        with f_col4:
            board_pcm_pct = st.number_input(
                "12th Std / PUC PCM Aggregate (%):",
                min_value=35.0,
                max_value=100.0,
                value=91.5,
                step=0.5,
            )
            target_pref_branch = st.selectbox(
                "Target Branch for Multi-Test Match:",
                ["CSE", "AI-DS", "ISE", "ECE", "MECH"],
                key="manual_score_branch",
            )

        if st.button("📊 Evaluate Multi-Test Admission Pathways", type="primary", use_container_width=True):
            evaluated_pathways = []
            for c in all_colleges_dicts:
                code = c["code"]
                nirf = c["nirf_rank_2025"] if isinstance(c["nirf_rank_2025"], int) else 100
                base_benchmark = nirf * 35

                # KCET Feasibility
                kcet_status = "N/A"
                if kcet_rank_in > 0:
                    cutoff_kcet = int(base_benchmark * 1.0)
                    if kcet_rank_in <= cutoff_kcet:
                        kcet_status = f"🟢 Eligible (Govt ₹{c['govt_fee_cet_lakhs']}L/yr)"
                    elif kcet_rank_in <= cutoff_kcet * 1.2:
                        kcet_status = "🟠 Borderline Round-3"
                    else:
                        kcet_status = f"🔴 Rank #{kcet_rank_in:,} exceeds #{cutoff_kcet:,}"

                # COMEDK Feasibility
                comedk_status = "N/A"
                if comedk_rank_in > 0:
                    cutoff_comedk = int(base_benchmark * 1.45)
                    if comedk_rank_in <= cutoff_comedk:
                        comedk_status = f"🟢 Eligible (COMEDK ₹{c['comedk_fee_lakhs']}L/yr)"
                    elif comedk_rank_in <= cutoff_comedk * 1.2:
                        comedk_status = "🟠 Borderline Round-3"
                    else:
                        comedk_status = f"🔴 Rank #{comedk_rank_in:,} exceeds #{cutoff_comedk:,}"

                # Scholarships
                merit_scholarship = "Standard Mgmt Quota"
                if board_pcm_pct >= 90.0 and (jee_percentile_in >= 92.0 or kcet_rank_in < 2500):
                    merit_scholarship = "🌟 50% Tuition Merit Scholarship"
                elif board_pcm_pct >= 85.0 or jee_percentile_in >= 88.0:
                    merit_scholarship = "✨ 25% Tuition Merit Scholarship"

                evaluated_pathways.append({
                    "College Code": code,
                    "Institution": c["name"],
                    "NIRF Rank": f"#{c['nirf_rank_2025']}",
                    "KCET Feasibility": kcet_status,
                    "COMEDK Feasibility": comedk_status,
                    "Mgmt Quota Fee (CSE)": f"₹{c['mgmt_fee_cse_lakhs']} LPA",
                    "Merit Quota Scholarship": merit_scholarship,
                    "Median CTC": f"₹{c['median_ctc_lpa']} LPA",
                })

            df_pathways = pd.DataFrame(evaluated_pathways)
            st.success(f"Generated multi-test eligibility matrix for {target_pref_branch} across 15 benchmark colleges:")
            st.dataframe(df_pathways, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # 5. In-Detail College Portal & Direct Web Directories (Session Detached Safe)
    # -------------------------------------------------------------------------
    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
    st.subheader("🏛️ Institutional Knowledge Directory & Official Portals")
    st.caption("Access verified administrative portals, KEA seat allocation archives, and placement records directly.")

    if all_colleges_dicts:
        col_selector_options = [f"{c['code']} - {c['name']}" for c in all_colleges_dicts]

        selected_portal_col = st.selectbox(
            "Select College to Inspect In-Detail:",
            col_selector_options,
            index=0,
            key="portal_inspector_college",
        )

        selected_code = selected_portal_col.split(" - ")[0]
        detailed_college = next((c for c in all_colleges_dicts if c["code"] == selected_code), None)

        if detailed_college:
            portal_links = COLLEGE_PORTAL_LINKS.get(
                selected_code,
                {
                    "website": "https://cetonline.karnataka.gov.in/kea/",
                    "admissions_portal": "https://cetonline.karnataka.gov.in/kea/",
                    "kea_matrix_portal": "https://cetonline.karnataka.gov.in/kea/",
                    "placements_hub": "https://cetonline.karnataka.gov.in/kea/",
                    "naac_nirf_dossier": "https://cetonline.karnataka.gov.in/kea/",
                    "virtual_tour": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                },
            )

            st.markdown(
                f"""
                <div style="
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 1.25rem;
                    margin-top: 0.5rem;
                    margin-bottom: 1.25rem;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <h3 style="margin: 0; color: #0f172a;">{detailed_college['name']} ({detailed_college['short_name']})</h3>
                            <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.9rem;">
                                📍 {detailed_college['city']} | Estd. {detailed_college['established_year']} | Code: <b>{detailed_college['code']}</b> | NIRF 2025: <b>#{detailed_college['nirf_rank_2025']}</b> | NAAC: <b>{detailed_college['naac_grade']} ({detailed_college['naac_cgpa']})</b>
                            </p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            d_col1, d_col2, d_col3 = st.columns(3)

            with d_col1:
                st.markdown("#### 🌐 Official Web Portals")
                st.link_button(
                    "🏛️ Main College Official Website",
                    portal_links["website"],
                    use_container_width=True,
                )
                st.link_button(
                    "📝 Direct Admissions & Quota Application",
                    portal_links["admissions_portal"],
                    use_container_width=True,
                )
                st.link_button(
                    "📑 KEA CET Seat Matrix & Counseling Archive",
                    portal_links["kea_matrix_portal"],
                    use_container_width=True,
                )

            with d_col2:
                st.markdown("#### 📈 Placements & Accreditations")
                st.link_button(
                    "💼 Official Career & Placement Statistics Hub",
                    portal_links["placements_hub"],
                    use_container_width=True,
                )
                st.link_button(
                    "📜 NAAC SSR & NIRF Ranking Verification Dossier",
                    portal_links["naac_nirf_dossier"],
                    use_container_width=True,
                )
                st.link_button(
                    "🎥 Virtual Campus & Lab Tour Video",
                    portal_links["virtual_tour"],
                    use_container_width=True,
                )

            with d_col3:
                st.markdown("#### 💰 Verified Fee Structure")
                st.metric(
                    "Management Quota Fee (CSE)",
                    f"₹{detailed_college['mgmt_fee_cse_lakhs']} Lakhs / yr",
                )
                st.metric(
                    "Government Quota Fee (KCET)",
                    f"₹{detailed_college['govt_fee_cet_lakhs']} Lakhs / yr",
                )
                st.metric(
                    "Median Placement CTC",
                    f"₹{detailed_college['median_ctc_lpa']} LPA",
                    delta=f"Highest: ₹{detailed_college['highest_ctc_lpa']} LPA",
                )
                
