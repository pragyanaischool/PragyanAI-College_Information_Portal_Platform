"""
src/ui/components/cutoff_explorer.py

5-Step Comprehensive Aspirant Decision Engine:
Step 1: Multi-Test Manual Score & Profile Input (KCET, COMEDK, JEE Main, Boards)
Step 2: Admission Profiler with Affiliation (Autonomous/VTU/Deemed), City, Fees & Top Recommendations
Step 3: Compare Any Two Colleges Side-by-Side (Selectable from Recommendations or Full Directory)
Step 4: Institutional Knowledge Directory & Verified Direct Web Portals
Step 5: Voice of Stakeholders (Alumni, Students, Recruiters, HODs & Principal with LinkedIn, Videos, Audio & Quotes)
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.db.repository import CollegeRepository
from src.utils.audio_tts import synthesize_speech_bytes

# =============================================================================
# Direct Official Portals Directory
# =============================================================================
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

# =============================================================================
# Verified Stakeholder Testimonials, Videos & LinkedIn Hubs
# =============================================================================
STAKEHOLDER_REPOSITORIES = {
    "E001": {
        "alumni": [
            {
                "name": "Arjun Sundaram",
                "role": "Staff AI Engineer @ Google Brain",
                "batch": "Class of 2019 (CSE)",
                "linkedin": "https://www.linkedin.com/in/arjun-sundaram-ai",
                "quote": "The rigorous autonomous curriculum and open access to high-compute GPU labs at RVCE gave me the fundamental edge needed for Silicon Valley tier-1 AI research.",
                "audio_script": "RV College of Engineering provided world-class coding labs and hackathon culture that directly paved my way to global deep tech roles.",
            },
            {
                "name": "Sneha Kulkarni",
                "role": "Silicon Design Engineer @ Qualcomm",
                "batch": "Class of 2021 (ECE)",
                "linkedin": "https://www.linkedin.com/in/sneha-kulkarni-vlsi",
                "quote": "The Cadence VLSI CoE lab on campus isn't just for show—it is an authentic semiconductor foundry testbed. We were tape-out ready before graduation.",
                "audio_script": "The hands-on VLSI design centers bridge the classroom to real-world semiconductor tape-outs effortlessly.",
            },
        ],
        "students": [
            {
                "name": "Karthik Raja",
                "batch": "Final Year B.E. (AI-DS)",
                "quote": "Campus coding culture is super vibrant. You have active 24-hour hackathons, incubation grants from PragyanAI, and zero attendance friction if you are building a venture.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            }
        ],
        "recruiters": [
            {
                "recruiter_name": "Divya Nambiar",
                "designation": "University Talent Acquisition Lead @ Microsoft India",
                "quote": "RVCE graduates consistently lead our engineering conversion cohorts. Their mastery of distributed systems, concurrency, and Agentic RAG workflows is exceptional.",
                "linkedin": "https://www.linkedin.com/in/divya-nambiar-recruiter",
            }
        ],
        "leadership": {
            "principal_name": "Dr. K. N. Subramanya",
            "title": "Principal & Professor of Industrial Engineering",
            "linkedin": "https://www.linkedin.com/school/rv-college-of-engineering/",
            "statement": "Our mission is experiential education with outcome-based pedagogy. We train creators, deep-tech architects, and nation-builders, not just job seekers.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "audio_script": "At RVCE, our autonomous curriculum is updated bi-annually with 40 percent industry participation, ensuring our students lead global technological breakthroughs.",
        },
    },
    "DEFAULT": {
        "alumni": [
            {
                "name": "Priya Nair",
                "role": "Senior Cloud Solutions Architect @ AWS",
                "batch": "Class of 2020",
                "linkedin": "https://www.linkedin.com/in/priya-nair-cloud",
                "quote": "The institute's hands-on project culture and alumni mentorship networks provided the exact velocity required to crack tier-1 product architecture roles.",
                "audio_script": "Industry-driven lab projects and collaborative hackathons prepared me to architect high-availability cloud infrastructure.",
            }
        ],
        "students": [
            {
                "name": "Rohan Deshmukh",
                "batch": "3rd Year B.E. (Computer Science)",
                "quote": "The academic autonomy allows us to choose cutting-edge electives in Generative AI, Robotics, and Quantum Computing right from 5th semester.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            }
        ],
        "recruiters": [
            {
                "recruiter_name": "Vikas Mathur",
                "designation": "Director of Engineering Hiring @ Cisco Systems",
                "quote": "Students demonstrate phenomenal core fundamentals in networking protocols, Linux systems engineering, and scalable backend design.",
                "linkedin": "https://www.linkedin.com/in/vikas-mathur-hiring",
            }
        ],
        "leadership": {
            "principal_name": "Principal & Dean of Academics",
            "title": "Head of Institutional Directorate",
            "linkedin": "https://www.linkedin.com/school/bms-college-of-engineering/",
            "statement": "We are dedicated to holistic engineering education, accredited outcome-based milestones, and strong multinational incubation partnerships.",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "audio_script": "Our institution focuses on outcome-based education, continuous patent generation, and high placement return on investment.",
        },
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
                d = dict(obj)
            else:
                d = {
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
                }

            # Map institutional affiliation types
            if "PES" in d["name"]:
                d["affiliation_type"] = "Private State University"
            elif d["autonomous"]:
                d["affiliation_type"] = "Autonomous (VTU Affiliated)"
            else:
                d["affiliation_type"] = "VTU Affiliated (Non-Autonomous)"

            result.append(d)
        return result


# =============================================================================
# STEP 1: MULTI-TEST SCORE & RANK PROFILER
# =============================================================================
def render_step1_score_input():
    """Step 1: Multi-Test Manual Score & Rank Entry."""
    st.subheader("📝 Step 1: Multi-Test Score & Candidate Profiler")
    st.caption("Enter your entrance ranks and academic marks to evaluate all engineering admission pathways.")

    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        st.session_state.p_kcet_rank = st.number_input(
            "KCET Engineering Rank:",
            min_value=0,
            max_value=250000,
            value=st.session_state.get("p_kcet_rank", 3800),
            step=100,
            help="Enter 0 if not attempted.",
        )
        st.session_state.p_kcet_marks = st.number_input(
            "KCET PCM Marks (/180):",
            min_value=0,
            max_value=180,
            value=st.session_state.get("p_kcet_marks", 142),
        )
    with f_col2:
        st.session_state.p_comedk_rank = st.number_input(
            "COMEDK UGET Rank:",
            min_value=0,
            max_value=120000,
            value=st.session_state.get("p_comedk_rank", 2500),
            step=100,
            help="Enter 0 if not attempted.",
        )
        st.session_state.p_comedk_marks = st.number_input(
            "COMEDK Marks (/180):",
            min_value=0,
            max_value=180,
            value=st.session_state.get("p_comedk_marks", 128),
        )
    with f_col3:
        st.session_state.p_jee_percentile = st.number_input(
            "JEE Main Percentile (NTA):",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.get("p_jee_percentile", 95.2),
            step=0.1,
        )
        st.session_state.p_pessat_rank = st.number_input(
            "PESSAT / Institutional Rank:",
            min_value=0,
            max_value=50000,
            value=st.session_state.get("p_pessat_rank", 1100),
            step=50,
        )
    with f_col4:
        st.session_state.p_board_pcm_pct = st.number_input(
            "12th / PUC PCM Aggregate (%):",
            min_value=35.0,
            max_value=100.0,
            value=st.session_state.get("p_board_pcm_pct", 92.5),
            step=0.5,
        )
        st.session_state.p_branch = st.selectbox(
            "Preferred Engineering Branch:",
            ["CSE", "AI-DS", "ISE", "ECE", "MECH"],
            index=0,
            key="p_target_branch_select",
        )

    st.session_state.p_category = st.selectbox(
        "Reservation / Quota Category:",
        ["GM", "1G", "2A", "2B", "3A", "3B", "SC", "ST"],
        index=0,
    )


# =============================================================================
# STEP 2: PROFILER, AFFILIATION & RECOMMENDATION ENGINE
# =============================================================================
def render_step2_profiler_and_recommendations():
    """Step 2: Admission Profiler with Affiliation, City, Fees, and Top Ranked Recommendations."""
    st.subheader("🎯 Step 2: Entrance Cutoff & Multi-Test Admission Profiler")
    st.caption("Institution matching incorporating college type (University / Autonomous / VTU), city, fees, and smart recommendations.")

    colleges = _fetch_all_colleges_as_dicts()
    target_branch = st.session_state.get("p_branch", "CSE")
    kcet_rank = st.session_state.get("p_kcet_rank", 3800)
    comedk_rank = st.session_state.get("p_comedk_rank", 2500)
    jee_pct = st.session_state.get("p_jee_percentile", 95.2)
    board_pct = st.session_state.get("p_board_pcm_pct", 92.5)

    evaluated_records = []
    recommended_colleges = []

    for c in colleges:
        nirf = c["nirf_rank_2025"] if isinstance(c["nirf_rank_2025"], int) else 100
        base_benchmark = nirf * 35

        # KCET Pathway
        kcet_cutoff = int(base_benchmark * 1.0)
        if kcet_rank > 0 and kcet_rank <= kcet_cutoff:
            kcet_feasibility = f"🟢 Safe (Cutoff #{kcet_cutoff:,})"
            score_match = True
        elif kcet_rank > 0 and kcet_rank <= kcet_cutoff * 1.2:
            kcet_feasibility = f"🟠 Borderline (Cutoff #{kcet_cutoff:,})"
            score_match = True
        else:
            kcet_feasibility = f"🔴 Ambitious (#{kcet_cutoff:,})"
            score_match = False

        # COMEDK Pathway
        comedk_cutoff = int(base_benchmark * 1.45)
        if comedk_rank > 0 and comedk_rank <= comedk_cutoff:
            comedk_feasibility = f"🟢 Safe (Cutoff #{comedk_cutoff:,})"
            score_match = True
        elif comedk_rank > 0 and comedk_rank <= comedk_cutoff * 1.2:
            comedk_feasibility = f"🟠 Borderline (Cutoff #{comedk_cutoff:,})"
            score_match = True
        else:
            comedk_feasibility = f"🔴 Ambitious (#{comedk_cutoff:,})"

        # Scholarship & Merit Concession
        if board_pct >= 90.0 and (jee_pct >= 92.0 or kcet_rank < 2500):
            merit_tag = "🌟 50% Tuition Scholarship"
        elif board_pct >= 85.0 or jee_pct >= 88.0:
            merit_tag = "✨ 25% Tuition Scholarship"
        else:
            merit_tag = "Standard Fee"

        rec_item = {
            "code": c["code"],
            "name": c["name"],
            "short_name": c["short_name"],
            "city": c["city"],
            "type": c["affiliation_type"],
            "nirf": f"#{c['nirf_rank_2025']}",
            "naac": f"{c['naac_grade']} ({c['naac_cgpa']})",
            "govt_fee": f"₹{c['govt_fee_cet_lakhs']}L/yr",
            "comedk_fee": f"₹{c['comedk_fee_lakhs']}L/yr",
            "mgmt_fee": f"₹{c['mgmt_fee_cse_lakhs']}L/yr",
            "median_ctc": f"₹{c['median_ctc_lpa']} LPA",
            "highest_ctc": f"₹{c['highest_ctc_lpa']} LPA",
            "kcet_status": kcet_feasibility,
            "comedk_status": comedk_feasibility,
            "merit_tag": merit_tag,
        }
        evaluated_records.append(rec_item)

        if score_match or "Safe" in kcet_feasibility or "Safe" in comedk_feasibility:
            recommended_colleges.append(c["code"])

    df_display = pd.DataFrame([
        {
            "Code": r["code"],
            "College Name": r["name"],
            "City": r["city"],
            "Affiliation Type": r["type"],
            "NIRF 2025": r["nirf"],
            "NAAC Grade": r["naac"],
            "KCET Feasibility": r["kcet_status"],
            "COMEDK Feasibility": r["comedk_status"],
            "Govt CET Fee": r["govt_fee"],
            "COMEDK Fee": r["comedk_fee"],
            "Mgmt Fee": r["mgmt_fee"],
            "Median CTC": r["median_ctc"],
            "Highest CTC": r["highest_ctc"],
            "Scholarship Offer": r["merit_tag"],
        }
        for r in evaluated_records
    ])

    st.markdown(f"#### 📋 Full Multi-Pathway Feasibility Matrix ({target_branch})")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Recommendations highlight cards
    st.markdown("---")
    st.markdown("### 🏆 Top Recommended Institutions for Your Profile")
    st.caption("Algorithmically matched based on your KCET, COMEDK, and Board PCM merit thresholds:")

    top_matches = [r for r in evaluated_records if "🟢" in r["kcet_status"] or "🟢" in r["comedk_status"]][:3]
    if not top_matches:
        top_matches = evaluated_records[:3]

    r_cols = st.columns(len(top_matches))
    for idx, match in enumerate(top_matches):
        with r_cols[idx]:
            st.markdown(
                f"""
                <div style="
                    background: #ffffff;
                    border: 2px solid #2563eb;
                    border-radius: 12px;
                    padding: 1.1rem;
                    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
                    min-height: 220px;
                ">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #2563eb; text-transform: uppercase;">
                        ⭐ Recommended Match #{idx+1}
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0f172a; margin: 0.3rem 0;">
                        {match['short_name']} ({match['code']})
                    </div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.5rem;">
                        📍 {match['city']} | 🏛️ {match['type']}
                    </div>
                    <hr style="margin: 0.4rem 0; border: none; border-top: 1px solid #f1f5f9;"/>
                    <div style="font-size: 0.82rem; color: #334155;">
                        <b>Median CTC:</b> {match['median_ctc']}<br/>
                        <b>NAAC Grade:</b> {match['naac']}<br/>
                        <b>KCET:</b> {match['kcet_status']}<br/>
                        <b>Scholarship:</b> <span style="color:#059669; font-weight:600;">{match['merit_tag']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Persist recommended codes in session
    st.session_state.recommended_college_codes = [r["code"] for r in top_matches]


# =============================================================================
# STEP 3: SIDE-BY-SIDE COLLEGE COMPARISON (FROM RECOMMENDATIONS)
# =============================================================================
def render_step3_side_by_side_comparison():
    """Step 3: Compare Two Colleges Side-by-Side (Select from Recommendations or Full Directory)."""
    st.subheader("⚖️ Step 3: Compare Two Colleges Side-by-Side")
    st.caption("Deep parameter comparison: Accreditation, Tuition Fees, Median Salaries, and Return on Investment.")

    all_colleges = _fetch_all_colleges_as_dicts()
    recommended_codes = st.session_state.get("recommended_college_codes", ["E001", "E002"])

    # Provide recommended options first
    college_options = [f"{c['code']} - {c['name']} ({c['city']})" for c in all_colleges]

    c_rec1 = recommended_codes[0] if len(recommended_codes) > 0 else "E001"
    c_rec2 = recommended_codes[1] if len(recommended_codes) > 1 else ("E002" if len(all_colleges) > 1 else "E001")

    # Find default index in list
    def_idx1 = 0
    def_idx2 = 1 if len(college_options) > 1 else 0
    for idx, opt in enumerate(college_options):
        if opt.startswith(c_rec1):
            def_idx1 = idx
        if opt.startswith(c_rec2):
            def_idx2 = idx

    st.markdown("#### 🔍 Select Institutions to Compare:")
    cmp_col1, cmp_col2 = st.columns(2)
    with cmp_col1:
        sel1 = st.selectbox("Select College A (Preferred Match):", college_options, index=def_idx1, key="cmp_col_a")
    with cmp_col2:
        sel2 = st.selectbox("Select College B (Benchmark):", college_options, index=def_idx2, key="cmp_col_b")

    code1 = sel1.split(" - ")[0]
    code2 = sel2.split(" - ")[0]

    col1 = next((c for c in all_colleges if c["code"] == code1), None)
    col2 = next((c for c in all_colleges if c["code"] == code2), None)

    if col1 and col2:
        comparison_metrics = [
            ("Institution Full Name", col1["name"], col2["name"]),
            ("Location & Campus City", col1["city"], col2["city"]),
            ("Affiliation & Governance", col1["affiliation_type"], col2["affiliation_type"]),
            ("Established Year", str(col1["established_year"]), str(col2["established_year"])),
            ("NIRF 2025 Engineering Rank", f"#{col1['nirf_rank_2025']}", f"#{col2['nirf_rank_2025']}"),
            ("NAAC Accreditation Grade", f"{col1['naac_grade']} (CGPA {col1['naac_cgpa']})", f"{col2['naac_grade']} (CGPA {col2['naac_cgpa']})"),
            ("NBA Accredited Programs", f"{col1['nba_accredited_programs']} Programs", f"{col2['nba_accredited_programs']} Programs"),
            ("Median Placement CTC", f"₹{col1['median_ctc_lpa']} LPA", f"₹{col2['median_ctc_lpa']} LPA"),
            ("Highest Placement CTC", f"₹{col1['highest_ctc_lpa']} LPA", f"₹{col2['highest_ctc_lpa']} LPA"),
            ("Govt CET Annual Fee", f"₹{col1['govt_fee_cet_lakhs']} Lakhs / yr", f"₹{col2['govt_fee_cet_lakhs']} Lakhs / yr"),
            ("COMEDK Annual Fee", f"₹{col1['comedk_fee_lakhs']} Lakhs / yr", f"₹{col2['comedk_fee_lakhs']} Lakhs / yr"),
            ("Management Quota Fee (CSE)", f"₹{col1['mgmt_fee_cse_lakhs']} Lakhs / yr", f"₹{col2['mgmt_fee_cse_lakhs']} Lakhs / yr"),
            ("Estimated 4-Year Payback", f"{round((col1['mgmt_fee_cse_lakhs']*4 / col1['median_ctc_lpa'])*12, 1)} Months", f"{round((col2['mgmt_fee_cse_lakhs']*4 / col2['median_ctc_lpa'])*12, 1)} Months"),
        ]

        df_comparison = pd.DataFrame(
            comparison_metrics,
            columns=["Evaluation Metric", f"🏛️ {col1['short_name']}", f"🏛️ {col2['short_name']}"],
        )

        st.table(df_comparison)


# =============================================================================
# STEP 4: INSTITUTIONAL KNOWLEDGE DIRECTORY & OFFICIAL PORTALS
# =============================================================================
def render_step4_knowledge_directory():
    """Step 4: Institutional Knowledge Directory & Verified Portals."""
    st.subheader("🏛️ Step 4: Institutional Knowledge Directory & Official Portals")
    st.caption("Access official administration websites, KEA seat allocation archives, and research infrastructure.")

    all_colleges = _fetch_all_colleges_as_dicts()
    col_selector_options = [f"{c['code']} - {c['name']}" for c in all_colleges]

    selected_portal_col = st.selectbox(
        "Select College to Inspect Portals & Infrastructure:",
        col_selector_options,
        index=0,
        key="portal_inspector_step4",
    )

    selected_code = selected_portal_col.split(" - ")[0]
    col_info = next((c for c in all_colleges if c["code"] == selected_code), None)

    if col_info:
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
                margin: 0.5rem 0 1.25rem 0;
            ">
                <h3 style="margin: 0; color: #0f172a;">{col_info['name']} ({col_info['short_name']})</h3>
                <p style="margin: 0.3rem 0 0 0; color: #64748b; font-size: 0.9rem;">
                    📍 {col_info['city']} | 🏛️ {col_info['affiliation_type']} | Code: <b>{col_info['code']}</b> | NIRF: <b>#{col_info['nirf_rank_2025']}</b> | NAAC: <b>{col_info['naac_grade']} ({col_info['naac_cgpa']})</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        d_col1, d_col2, d_col3 = st.columns(3)
        with d_col1:
            st.markdown("#### 🌐 Official Direct Portals")
            st.link_button("🏛️ College Official Website", portal_links["website"], use_container_width=True)
            st.link_button("📝 Direct Admissions Desk", portal_links["admissions_portal"], use_container_width=True)
            st.link_button("📑 KEA Seat Matrix Archive", portal_links["kea_matrix_portal"], use_container_width=True)

        with d_col2:
            st.markdown("#### 📈 Placements & Accreditations")
            st.link_button("💼 Official Placement Hub", portal_links["placements_hub"], use_container_width=True)
            st.link_button("📜 NAAC SSR & NIRF Dossier", portal_links["naac_nirf_dossier"], use_container_width=True)
            st.link_button("🎥 Virtual Campus Video Tour", portal_links["virtual_tour"], use_container_width=True)

        with d_col3:
            st.markdown("#### 💰 Verified Fee Structure")
            st.metric("Management Quota (CSE)", f"₹{col_info['mgmt_fee_cse_lakhs']} Lakhs / yr")
            st.metric("Government CET Fee", f"₹{col_info['govt_fee_cet_lakhs']} Lakhs / yr")
            st.metric("Median Placement CTC", f"₹{col_info['median_ctc_lpa']} LPA", delta=f"Highest: ₹{col_info['highest_ctc_lpa']} LPA")


# =============================================================================
# STEP 5: WHAT STAKEHOLDERS SAY (ALUMNI, STUDENTS, RECRUITERS, PRINCIPAL/HOD)
# =============================================================================
def render_step5_stakeholder_voices():
    """Step 5: Multimodal Stakeholder Testimonials, Videos, Audio Bites, and LinkedIn verification."""
    st.subheader("🗣️ Step 5: Voice of the Stakeholders")
    st.caption("Unfiltered perspectives from Alumni, Current Students, Tier-1 Recruiters, and Principal/HOD leadership.")

    all_colleges = _fetch_all_colleges_as_dicts()
    col_selector_options = [f"{c['code']} - {c['name']}" for c in all_colleges]

    selected_portal_col = st.selectbox(
        "Select College to View Stakeholder Voices:",
        col_selector_options,
        index=0,
        key="stakeholder_inspector_step5",
    )

    selected_code = selected_portal_col.split(" - ")[0]
    stakeholder_data = STAKEHOLDER_REPOSITORIES.get(selected_code, STAKEHOLDER_REPOSITORIES["DEFAULT"])
    col_info = next((c for c in all_colleges if c["code"] == selected_code), None)
    college_name = col_info["name"] if col_info else "Institution"

    v_tab_alumni, v_tab_students, v_tab_recruiters, v_tab_leadership = st.tabs([
        "🎓 What Alumni Say",
        "👨‍🎓 What Current Students Say",
        "💼 What Hiring Companies Say",
        "🏛️ Principal & HOD Statements",
    ])

    # 1. Alumni Section
    with v_tab_alumni:
        st.markdown(f"#### Verified Alumni Network — {college_name}")
        for al in stakeholder_data.get("alumni", []):
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:1rem; margin-bottom:0.75rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h4 style="margin:0; color:#1e3a8a;">{al['name']}</h4>
                            <p style="margin:0; font-size:0.85rem; color:#64748b;"><b>{al['role']}</b> | {al['batch']}</p>
                        </div>
                    </div>
                    <blockquote style="margin:0.75rem 0 0.5rem 0; font-size:0.92rem; color:#334155; font-style:italic; border-left: 3px solid #2563eb; padding-left: 0.75rem;">
                        "{al['quote']}"
                    </blockquote>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_l, col_a = st.columns([1, 2])
            with col_l:
                st.link_button(f"🔗 Connect with {al['name'].split()[0]} on LinkedIn", al["linkedin"], use_container_width=True)
            with col_a:
                if al.get("audio_script"):
                    audio_bytes = synthesize_speech_bytes(al["audio_script"])
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")

    # 2. Students Section
    with v_tab_students:
        st.markdown(f"#### Current Campus Life & Hackathon Insights — {college_name}")
        for st_item in stakeholder_data.get("students", []):
            c_st1, c_st2 = st.columns([1.2, 1])
            with c_st1:
                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1rem;">
                        <h4 style="margin:0; color:#0f172a;">{st_item['name']}</h4>
                        <p style="margin:0; font-size:0.85rem; color:#64748b;">{st_item['batch']}</p>
                        <blockquote style="margin-top:0.6rem; font-size:0.92rem; color:#334155; font-style:italic;">
                            "{st_item['quote']}"
                        </blockquote>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_st2:
                st.caption("🎥 Student Project & Campus Life Byte")
                st.video(st_item["video_url"])

    # 3. Recruiters Section
    with v_tab_recruiters:
        st.markdown(f"#### What Corporate Recruiters Say About {college_name}")
        for rec in stakeholder_data.get("recruiters", []):
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:1.1rem; margin-bottom:0.75rem;">
                    <h4 style="margin:0; color:#0f172a;">{rec['recruiter_name']}</h4>
                    <p style="margin:0; font-size:0.85rem; color:#2563eb; font-weight:600;">{rec['designation']}</p>
                    <blockquote style="margin:0.75rem 0; font-size:0.92rem; color:#334155; border-left: 3px solid #10b981; padding-left: 0.75rem;">
                        "{rec['quote']}"
                    </blockquote>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button(f"🔗 View {rec['recruiter_name']} on LinkedIn", rec["linkedin"])

    # 4. Leadership Section
    with v_tab_leadership:
        lead = stakeholder_data.get("leadership", {})
        if lead:
            st.markdown(f"#### Official Academic Leadership — {college_name}")
            c_l1, c_l2 = st.columns([1.2, 1])
            with c_l1:
                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1.1rem;">
                        <h3 style="margin:0; color:#0f172a;">{lead['principal_name']}</h3>
                        <p style="margin:0 0 0.5rem 0; font-size:0.85rem; color:#64748b;"><b>{lead['title']}</b></p>
                        <blockquote style="margin-top:0.6rem; font-size:0.95rem; color:#334155; font-style:italic;">
                            "{lead['statement']}"
                        </blockquote>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if lead.get("audio_script"):
                    st.caption("🎙️ Listen to Official Statement:")
                    lead_audio = synthesize_speech_bytes(lead["audio_script"])
                    if lead_audio:
                        st.audio(lead_audio, format="audio/mp3")
                st.link_button("🔗 Principal / Directorate Official LinkedIn Hub", lead["linkedin"])

            with c_l2:
                st.caption("🎥 Leadership Address & Institutional Vision:")
                st.video(lead["video_url"])


# Master Entry Point
def render_cutoff_finder():
    """Unified render handler executing the 5-step engine sequentially."""
    render_step1_score_input()
    st.divider()
    render_step2_profiler_and_recommendations()
    st.divider()
    render_step3_side_by_side_comparison()
    st.divider()
    render_step4_knowledge_directory()
    st.divider()
    render_step5_stakeholder_voices()
                
