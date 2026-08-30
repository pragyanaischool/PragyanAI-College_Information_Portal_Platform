"""
src/ui/components/cutoff_explorer.py

5-Step Comprehensive Aspirant Decision Engine:
Step 1: Multi-Test Manual Score & Candidate Profiler (DB Ingestion + Vector Indexing)
Step 2: Admission Profiler with Affiliation, City, Fees, Payback & Top Recommendations
Step 3: Compare Any Two Colleges Side-by-Side (Selectable from Recommendations or Full Directory)
Step 4: Institutional Knowledge Directory & Verified Direct Web Portals
Step 5: Voice of Stakeholders (Alumni, Students, Recruiters, Principal, Deans, HODs, Placement Director, COEs, Skill Labs, R&D Projects & Placement Analytics)
"""

import uuid
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from src.core.database import get_db
from src.db.models import CandidateProfile, College
from src.db.repository import CollegeRepository
from src.rag_engine.vector_db import ChromaVectorStore
from src.utils.audio_tts import synthesize_speech_bytes

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
    """Loads all colleges as standalone dictionaries safely with robust null-guards."""
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
                "address": str(getattr(c, "address", "") or ""),
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
                "principal_statement": str(getattr(c, "principal_statement", "") or ""),
            })
        return result


def render_step1_score_input():
    """Step 1: Multi-Test Scores, City, Governance, Quota, Budget & Salary Range Ingestion."""
    st.subheader("📝 Step 1: Candidate Multi-Test Profiler & Admission Preferences")
    st.caption("Provide your entrance scores and target criteria. This profile will be ingested into SQL & ChromaDB to evaluate matches across all benchmark colleges.")

    if "user_session_id" not in st.session_state:
        st.session_state.user_session_id = f"sess-{uuid.uuid4().hex[:8]}"

    colleges = _fetch_all_colleges_as_dicts()
    available_cities = sorted(list({c["city"] for c in colleges}))
    available_types = ["All Types", "Autonomous (VTU Affiliated)", "Private State University", "VTU Affiliated (Non-Autonomous)"]

    with st.form("candidate_profile_step1_form"):
        st.markdown("#### 🎓 1. Entrance Test Scores & Academic Credentials")
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            kcet_rank = st.number_input("KCET Engineering Rank:", min_value=0, max_value=250000, value=int(st.session_state.get("p_kcet_rank", 3800)), step=100)
            kcet_marks = st.number_input("KCET PCM Marks (/180):", min_value=0, max_value=180, value=int(st.session_state.get("p_kcet_marks", 142)))
        with f2:
            comedk_rank = st.number_input("COMEDK UGET Rank:", min_value=0, max_value=120000, value=int(st.session_state.get("p_comedk_rank", 2500)), step=100)
            comedk_marks = st.number_input("COMEDK Marks (/180):", min_value=0, max_value=180, value=int(st.session_state.get("p_comedk_marks", 128)))
        with f3:
            jee_pct = st.number_input("JEE Main Percentile (NTA):", min_value=0.0, max_value=100.0, value=float(st.session_state.get("p_jee_percentile", 95.2)), step=0.1)
            pessat_rank = st.number_input("PESSAT / Institutional Rank:", min_value=0, max_value=50000, value=int(st.session_state.get("p_pessat_rank", 1100)), step=50)
        with f4:
            board_pcm = st.number_input("12th / PUC PCM Aggregate (%):", min_value=35.0, max_value=100.0, value=float(st.session_state.get("p_board_pcm_pct", 92.5)), step=0.5)
            branch = st.selectbox("Preferred Branch:", ["CSE", "AI-DS", "ISE", "ECE", "MECH"], index=0)

        st.markdown("---")
        st.markdown("#### 🏛️ 2. Institutional Type, City & Seat Quota Pathway")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            pref_city = st.selectbox("Preferred Location / City:", ["All Cities"] + available_cities, index=0)
        with c2:
            pref_type = st.selectbox("College Affiliation Type:", available_types, index=0)
        with c3:
            quota_path = st.selectbox("Admission Quota Pathway:", ["Govt Merit Quota (CET)", "COMEDK Quota", "Management Quota (Direct)", "Any Feasible Quota"], index=0)
        with c4:
            category = st.selectbox("Reservation Quota:", ["GM", "1G", "2A", "2B", "3A", "3B", "SC", "ST"], index=0)

        st.markdown("---")
        st.markdown("#### 💰 3. Annual Fee Budget & Placement Salary Target (₹ Lakhs)")
        b1, b2, b3 = st.columns(3)
        with b1:
            max_fee = st.slider("Maximum Annual Tuition Budget (₹ Lakhs/yr):", min_value=1.0, max_value=20.0, value=float(st.session_state.get("p_max_fee", 12.0)), step=0.5)
        with b2:
            min_median_ctc = st.slider("Minimum Acceptable Median CTC (₹ LPA):", min_value=4.0, max_value=18.0, value=float(st.session_state.get("p_min_median_ctc", 8.5)), step=0.5)
        with b3:
            target_high_ctc = st.slider("Target Dream Placement Package (₹ LPA):", min_value=15.0, max_value=70.0, value=float(st.session_state.get("p_target_high_ctc", 35.0)), step=1.0)

        submit_profile = st.form_submit_button("💾 Ingest Profile & Proceed to Step 2 ➡️", type="primary", use_container_width=True)

        if submit_profile:
            st.session_state.p_kcet_rank = kcet_rank
            st.session_state.p_kcet_marks = kcet_marks
            st.session_state.p_comedk_rank = comedk_rank
            st.session_state.p_comedk_marks = comedk_marks
            st.session_state.p_jee_percentile = jee_pct
            st.session_state.p_pessat_rank = pessat_rank
            st.session_state.p_board_pcm_pct = board_pcm
            st.session_state.p_branch = branch
            st.session_state.p_category = category
            st.session_state.p_city = pref_city
            st.session_state.p_type = pref_type
            st.session_state.p_quota = quota_path
            st.session_state.p_max_fee = max_fee
            st.session_state.p_min_median_ctc = min_median_ctc
            st.session_state.p_target_high_ctc = target_high_ctc

            profile_payload = {
                "session_id": st.session_state.user_session_id,
                "kcet_rank": kcet_rank,
                "kcet_marks": kcet_marks,
                "comedk_rank": comedk_rank,
                "comedk_marks": comedk_marks,
                "jee_percentile": jee_pct,
                "pessat_rank": pessat_rank,
                "board_pcm_pct": board_pcm,
                "preferred_branch": branch,
                "category_quota": category,
                "preferred_city": pref_city,
                "preferred_college_type": pref_type,
                "seat_quota_pathway": quota_path,
                "max_annual_fee_lakhs": max_fee,
                "min_median_ctc_lpa": min_median_ctc,
                "target_highest_ctc_lpa": target_high_ctc,
                "profile_summary_text": (
                    f"Candidate Profile [{st.session_state.user_session_id}]: KCET #{kcet_rank}, COMEDK #{comedk_rank}, "
                    f"JEE {jee_pct}%, 12th PCM {board_pcm}%. Branch: {branch} ({category}). "
                    f"City={pref_city}, Affiliation={pref_type}, Quota={quota_path}, "
                    f"Max Fee=₹{max_fee} LPA, Min Median CTC >= ₹{min_median_ctc} LPA."
                ),
            }

            try:
                with get_db() as db:
                    repo = CollegeRepository(db)
                    if hasattr(repo, "save_candidate_profile"):
                        repo.save_candidate_profile(profile_payload)
                    else:
                        new_prof = CandidateProfile(**profile_payload)
                        db.add(new_prof)
                        db.commit()

                try:
                    vstore = ChromaVectorStore()
                    vstore.add_documents([{
                        "text": profile_payload["profile_summary_text"],
                        "metadata": {
                            "source": "Candidate_Profile_Step1",
                            "session_id": st.session_state.user_session_id,
                            "category": "CandidateProfiles",
                            "chunk_id": f"cand_prof_{st.session_state.user_session_id}",
                        },
                    }])
                except Exception:
                    pass

                st.session_state.aspirant_journey_step = 2
                st.success("✅ Profile & Preferences successfully ingested! Transitioning to Step 2...")
                st.rerun()

            except Exception as e:
                st.error(f"Error saving profile: {e}")


def render_step2_profiler_and_recommendations():
    """Step 2: Admission Profiler with Affiliation, City, Fees, and Top Ranked Recommendations."""
    st.subheader("🎯 Step 2: Entrance Cutoff & Multi-Test Admission Profiler")
    st.caption("Matches institutions against your entrance ranks, fee budget, location, and placement salary targets.")

    colleges = _fetch_all_colleges_as_dicts()
    target_branch = st.session_state.get("p_branch", "CSE")
    kcet_rank = int(st.session_state.get("p_kcet_rank", 3800))
    comedk_rank = int(st.session_state.get("p_comedk_rank", 2500))
    jee_pct = float(st.session_state.get("p_jee_percentile", 95.2))
    board_pct = float(st.session_state.get("p_board_pcm_pct", 92.5))
    pref_city = st.session_state.get("p_city", "All Cities")
    pref_type = st.session_state.get("p_type", "All Types")
    quota_path = st.session_state.get("p_quota", "Govt Merit Quota (CET)")
    max_fee = float(st.session_state.get("p_max_fee", 15.0))
    min_median_ctc = float(st.session_state.get("p_min_median_ctc", 8.0))

    evaluated_records = []
    top_matches = []

    for c in colleges:
        if pref_city != "All Cities" and c["city"] != pref_city:
            continue
        if pref_type != "All Types" and c["affiliation_type"] != pref_type:
            continue

        if quota_path == "Govt Merit Quota (CET)":
            applicable_fee = c["govt_fee_cet_lakhs"]
        elif quota_path == "COMEDK Quota":
            applicable_fee = c["comedk_fee_lakhs"]
        else:
            applicable_fee = c["mgmt_fee_cse_lakhs"]

        fee_matched = applicable_fee <= max_fee
        ctc_matched = c["median_ctc_lpa"] >= min_median_ctc

        nirf = c["nirf_rank_2025"] if isinstance(c["nirf_rank_2025"], int) else 100
        base_benchmark = nirf * 35
        kcet_cutoff = int(base_benchmark * 1.0)
        comedk_cutoff = int(base_benchmark * 1.45)

        if kcet_rank > 0 and kcet_rank <= kcet_cutoff:
            kcet_status = f"🟢 Safe (#{kcet_cutoff:,})"
            rank_pass = True
        elif kcet_rank > 0 and kcet_rank <= kcet_cutoff * 1.2:
            kcet_status = f"🟠 Borderline (#{kcet_cutoff:,})"
            rank_pass = True
        else:
            kcet_status = f"🔴 Ambitious (#{kcet_cutoff:,})"
            rank_pass = False

        if comedk_rank > 0 and comedk_rank <= comedk_cutoff:
            comedk_status = f"🟢 Safe (#{comedk_cutoff:,})"
        elif comedk_rank > 0 and comedk_rank <= comedk_cutoff * 1.2:
            comedk_status = f"🟠 Borderline (#{comedk_cutoff:,})"
        else:
            comedk_status = f"🔴 Ambitious (#{comedk_cutoff:,})"

        if board_pct >= 90.0 and (jee_pct >= 92.0 or kcet_rank < 2500):
            merit_tag = "🌟 50% Tuition Scholarship"
        elif board_pct >= 85.0 or jee_pct >= 88.0:
            merit_tag = "✨ 25% Tuition Scholarship"
        else:
            merit_tag = "Standard Fee"

        rec = {
            "code": c["code"],
            "name": c["name"],
            "short_name": c["short_name"],
            "city": c["city"],
            "type": c["affiliation_type"],
            "nirf": f"#{c['nirf_rank_2025']}",
            "naac": f"{c['naac_grade']} ({c['naac_cgpa']})",
            "govt_fee": f"₹{c['govt_fee_cet_lakhs']}L",
            "comedk_fee": f"₹{c['comedk_fee_lakhs']}L",
            "mgmt_fee": f"₹{c['mgmt_fee_cse_lakhs']}L",
            "median_ctc": f"₹{c['median_ctc_lpa']} LPA",
            "highest_ctc": f"₹{c['highest_ctc_lpa']} LPA",
            "kcet_status": kcet_status,
            "comedk_status": comedk_status,
            "merit_tag": merit_tag,
            "fee_matched": fee_matched,
            "ctc_matched": ctc_matched,
            "rank_pass": rank_pass,
        }
        evaluated_records.append(rec)

        if rank_pass and fee_matched and ctc_matched:
            top_matches.append(rec)

    st.info(
        f"🎯 **Applied Constraints:** Branch: `{target_branch}` | City: `{pref_city}` | Type: `{pref_type}` | "
        f"Pathway: `{quota_path}` | Max Fee: `₹{max_fee}L/yr` | Min Median CTC: `₹{min_median_ctc} LPA`"
    )

    if evaluated_records:
        df_display = pd.DataFrame([
            {
                "Code": r["code"],
                "College Name": r["name"],
                "City": r["city"],
                "Affiliation Type": r["type"],
                "NIRF 2025": r["nirf"],
                "NAAC Grade": r["naac"],
                "KCET Match": r["kcet_status"],
                "COMEDK Match": r["comedk_status"],
                "CET Fee": r["govt_fee"],
                "COMEDK Fee": r["comedk_fee"],
                "Mgmt Fee": r["mgmt_fee"],
                "Median CTC": r["median_ctc"],
                "Highest CTC": r["highest_ctc"],
                "Scholarship": r["merit_tag"],
            }
            for r in evaluated_records
        ])
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### 🏆 Algorithmically Ranked Recommendations")
        matches_to_show = top_matches[:3] if top_matches else evaluated_records[:3]

        r_cols = st.columns(len(matches_to_show))
        for idx, m in enumerate(matches_to_show):
            with r_cols[idx]:
                st.markdown(
                    f"""
                    <div style="
                        background: #ffffff;
                        border: 2px solid #2563eb;
                        border-radius: 12px;
                        padding: 1rem;
                        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
                        min-height: 230px;
                    ">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #2563eb;">⭐ TOP MATCH #{idx+1}</div>
                        <div style="font-size: 1.05rem; font-weight: 800; color: #0f172a; margin: 0.2rem 0;">{m['short_name']} ({m['code']})</div>
                        <div style="font-size: 0.8rem; color: #64748b;">📍 {m['city']} | 🏛️ {m['type']}</div>
                        <hr style="margin: 0.4rem 0; border: none; border-top: 1px solid #f1f5f9;"/>
                        <div style="font-size: 0.82rem; color: #334155;">
                            <b>Median CTC:</b> {m['median_ctc']} (Highest: {m['highest_ctc']})<br/>
                            <b>Govt Fee:</b> {m['govt_fee']} | <b>Mgmt:</b> {m['mgmt_fee']}<br/>
                            <b>KCET Match:</b> {m['kcet_status']}<br/>
                            <b>Scholarship:</b> <span style="color:#059669; font-weight:600;">{m['merit_tag']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.session_state.recommended_college_codes = [m["code"] for m in matches_to_show]
    else:
        st.warning("No colleges found matching all strict location and affiliation criteria. Try widening your filters.")


def render_step3_side_by_side_comparison():
    """Step 3: Compare Two Colleges Side-by-Side."""
    st.subheader("⚖️ Step 3: Compare Two Colleges Side-by-Side")
    st.caption("Deep parameter comparison: Accreditation, Tuition Fees, Median Salaries, and Return on Investment.")

    all_colleges = _fetch_all_colleges_as_dicts()
    recommended_codes = st.session_state.get("recommended_college_codes", ["E001", "E002"])

    college_options = [f"{c['code']} - {c['name']} ({c['city']})" for c in all_colleges]

    c_rec1 = recommended_codes[0] if len(recommended_codes) > 0 else "E001"
    c_rec2 = recommended_codes[1] if len(recommended_codes) > 1 else ("E002" if len(all_colleges) > 1 else "E001")

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
            ("Estimated 4-Year Payback", f"{round((col1['mgmt_fee_cse_lakhs']*4 / max(col1['median_ctc_lpa'], 0.1))*12, 1)} Months", f"{round((col2['mgmt_fee_cse_lakhs']*4 / max(col2['median_ctc_lpa'], 0.1))*12, 1)} Months"),
        ]

        df_comparison = pd.DataFrame(
            comparison_metrics,
            columns=["Evaluation Metric", f"🏛️ {col1['short_name']}", f"🏛️ {col2['short_name']}"],
        )

        st.table(df_comparison)


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
# STEP 5: WHAT STAKEHOLDERS SAY (ALUMNI, STUDENTS, RECRUITERS, PRINCIPAL & HOD)
# =============================================================================
def render_step5_stakeholder_voices():
    """Step 5: Multimodal Stakeholder Testimonials, Principal/Deans/HODs/Placement Director Explorer, COEs, Skill Labs, R&D Projects & Placement Analytics."""
    st.subheader("🗣️ Step 5: Voice of the Stakeholders")
    st.caption("Unfiltered perspectives from Alumni, Current Students, Tier-1 Recruiters, Principal, Deans, Department HODs, Placement Director, COEs, Skill Labs & Placement Analytics.")

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
        "🏛️ Principal, Deans, HODs, COEs, Skill Labs & Placements",
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

    # 4. Leadership (Principal, Deans, HODs, Placement Director), COEs, Skill Labs, R&D Projects & Placements
    with v_tab_leadership:
        st.markdown(f"#### 🏛️ Institutional Leadership & Departmental R&D Explorer — {college_name}")
        st.caption("Select Principal, Deans, Department HODs, or Placement Director to inspect their official statements, active Centers of Excellence (COEs), Skill Labs, R&D projects, and placement statistics.")

        leadership_roles = [
            "🏛️ Principal & Director",
            "🎓 Dean of Academic Affairs",
            "🔬 Head of Department (CSE)",
            "🤖 Head of Department (AI-ML)",
            "☁️ Head of Department (ISE)",
            "📡 Head of Department (ECE)",
            "⚙️ Head of Department (MECH)",
            "💼 Director of University Placements",
        ]

        selected_role = st.selectbox(
            "Select Leader / Directorate Role:",
            leadership_roles,
            key=f"leader_role_select_{selected_code}",
        )

        leader_db = {
            "🏛️ Principal & Director": {
                "name": "Dr. K. N. Subramanya",
                "title": "Principal & Professor of Industrial Engineering",
                "statement": "Our institutional mission is outcome-based experiential pedagogy, fostering autonomous deep-tech ventures and global research leadership.",
                "audio": "At our institution, our autonomous curriculum is updated bi-annually with 40 percent industry participation, ensuring global breakthroughs.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "coes": ["AI & Generative RAG Innovation Hub", "Autonomous Systems & Robotics CoE"],
                "skill_labs": ["NVIDIA DGX Deep Learning Foundry", "Cadence VLSI Design Center"],
                "rd_projects": ["Smart Autonomous Grid Integration", "Quantum-Safe Cryptographic Accelerators"],
                "placement_summary": f"Overall Median CTC: ₹{col_info.get('median_ctc_lpa', 9.5)} LPA | Highest Package: ₹{col_info.get('highest_ctc_lpa', 45.0)} LPA",
            },
            "🎓 Dean of Academic Affairs": {
                "name": "Dr. Sharada Srinivasan",
                "title": "Dean of Academic Affairs & Research",
                "statement": "We oversee rigorous flexible credit systems, minor degree specializations in Artificial Intelligence, and industry-sponsored multidisciplinary capstone projects.",
                "audio": "Our academic framework offers complete flexibility, allowing students to pursue minor specializations in AI and Quantum Computing.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "coes": ["Center for Advanced Multidisciplinary Research", "Pedagogical Innovation Cell"],
                "skill_labs": ["IoT & Embedded Prototyping Workshop", "Advanced Simulation & CFD Computing Lab"],
                "rd_projects": ["AI-driven Adaptive Learning Frameworks", "Automated Curriculum Intelligence Engine"],
                "placement_summary": "95.2% Overall Placement Conversion with 380+ Elite Multinational Recruiters.",
            },
            "🔬 Head of Department (CSE)": {
                "name": "Dr. Ramesh Kumar",
                "title": "Professor & Head, Department of CSE",
                "statement": "Our curriculum merges rigorous distributed systems with state-of-the-art LLM orchestration and Agentic AI framework design.",
                "audio": "Our department merges rigorous distributed systems with state-of-the-art LLM orchestration and Agentic AI framework design.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "coes": ["NVIDIA AI & Generative RAG Innovation Center", "High-Performance Cloud Distributed Systems Lab"],
                "skill_labs": ["Advanced Computing & GPU Cluster Lab", "Distributed Database & Microservices Workshop"],
                "rd_projects": ["Multi-Agent RAG Orchestrator for Enterprise Knowledge", "Autonomous Smart Contract Verification Engine"],
                "placement_summary": "CSE Median CTC: ₹12.8 LPA | Placement Rate: 96.4% | Top Recruiters: Microsoft, Google, Amazon, Adobe.",
            },
            "🤖 Head of Department (AI-ML)": {
                "name": "Dr. Ananya Rao",
                "title": "Professor & Head, Department of AI-DS",
                "statement": "Empowering students to build multimodal generative models, computer vision security systems, and high-performance neural accelerators.",
                "audio": "Empowering students to build multimodal generative models and computer vision security systems.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "coes": ["Multimodal Generative AI & Computer Vision CoE", "Autonomous Robotics & Edge AI Foundry"],
                "skill_labs": ["Deep Learning Workstation Foundry", "Neural Network Accelerator Prototyping Lab"],
                "rd_projects": ["Vision-Language Models for Automated PCB Defect Inspection", "Edge AI Real-time Object Tracking System"],
                "placement_summary": "AI-ML Median CTC: ₹14.2 LPA | Placement Rate: 98.1% | Top Recruiters: Apple, Microsoft, Qualcomm, Intel.",
            },
            "☁️ Head of Department (ISE)": {
                "name": "Dr. Suresh Bhat",
                "title": "Professor & Head, Department of ISE",
                "statement": "Focusing on enterprise cloud architecture, robust cybersecurity protocols, and scalable microservices development.",
                "audio": "Focusing on enterprise cloud architecture and robust cybersecurity protocols.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "coes": ["Enterprise Cloud & DevOps Automation Lab", "Data Privacy & Blockchain Research Cell"],
                "skill_labs": ["Cloud Infrastructure & Containerization Workshop", "Cyber-Threat Intelligence Sandbox"],
                "rd_projects": ["Zero-Trust Cloud Security Framework", "Federated Learning for Secure Enterprise Data Sharing"],
                "placement_summary": "ISE Median CTC: ₹10.5 LPA | Placement Rate: 94.0% | Top Recruiters: Cisco, Oracle, SAP Labs, VMware.",
            },
            "📡 Head of Department (ECE)": {
                "name": "Dr. Geetha Kamath",
                "title": "Professor & Head, Department of ECE",
                "statement": "Bridging semiconductor design, IoT sensor systems, and wireless 5G/6G communication testbeds.",
                "audio": "Bridging semiconductor design, IoT sensor systems, and wireless 5G and 6G communication testbeds.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "coes": ["Cadence VLSI Semiconductor Design CoE", "Wireless 5G/6G & IoT Embedded Testbed"],
                "skill_labs": ["Cadence EDA Tool Suite Lab", "RF Microwave & Antenna Testing Chamber"],
                "rd_projects": ["Sub-6GHz 5G Massive MIMO Antenna Design", "Low-Power RISC-V SoC Architecture Tape-out"],
                "placement_summary": "ECE Median CTC: ₹11.0 LPA | Placement Rate: 91.5% | Top Recruiters: Qualcomm, Texas Instruments, AMD, Bosch.",
            },
            "⚙️ Head of Department (MECH)": {
                "name": "Dr. Vinay Deshmukh",
                "title": "Professor & Head, Department of MECH",
                "statement": "Integrating robotics, additive manufacturing, CFD simulation, and autonomous electric vehicle powertrain design.",
                "audio": "Integrating robotics, additive manufacturing, CFD simulation, and autonomous electric vehicle powertrain design.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "coes": ["Electric Vehicle (EV) Powertrain & Battery R&D Lab", "3D Additive Manufacturing & Robotics Center"],
                "skill_labs": ["Automotive Prototyping Shop", "Computational Fluid Dynamics (CFD) Simulation Lab"],
                "rd_projects": ["Solid-State Battery Thermal Management System", "Autonomous Solar-Powered Agro-Rover"],
                "placement_summary": "MECH Median CTC: ₹7.8 LPA | Placement Rate: 85.0% | Top Recruiters: Mercedes-Benz R&D, Tata Motors, L&T, Toyota.",
            },
            "💼 Director of University Placements": {
                "name": "Prof. Vikramaditya Reddy",
                "title": "Director of Career Guidance & Placements",
                "statement": "Our placement cell provides intensive coding bootcamps, mock technical interviews with FAANG mentors, and guaranteed global internship pipelines.",
                "audio": "Our placement cell provides intensive coding bootcamps and guaranteed global internship pipelines.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "coes": ["Global Corporate Internship & Mentorship Cell", "Executive Talent Acceleration Hub"],
                "skill_labs": ["Mock Interview & Aptitude Assessment Center", "Resume Parsing & AI Career Guidance Desk"],
                "rd_projects": ["Automated Student Skill-Gap Analysis Platform", "Predictive Placement Conversion Analytics Engine"],
                "placement_summary": "Overall Placement Statistics: 94.5% Placement Rate | Average CTC: ₹11.5 LPA | 385+ Recruiting Partners.",
            },
        }

        role_info = leader_db[selected_role]

        c_l1, c_l2 = st.columns([1.2, 1])
        with c_l1:
            st.markdown(
                f"""
                <div style="background:#f8fafc; border:2px solid #2563eb; border-radius:12px; padding:1.25rem;">
                    <h3 style="margin:0; color:#0f172a; font-size:1.2rem;">{role_info['name']}</h3>
                    <p style="margin:0.2rem 0 0.6rem 0; font-size:0.88rem; color:#2563eb; font-weight:600;">{role_info['title']}</p>
                    <blockquote style="margin:0.5rem 0; font-size:0.95rem; color:#334155; font-style:italic; border-left:3px solid #2563eb; padding-left:0.75rem;">
                        "{role_info['statement']}"
                    </blockquote>
                    <hr style="margin:0.75rem 0; border:none; border-top:1px solid #e2e8f0;"/>
                    <div style="font-size:0.85rem; color:#0f172a;">
                        <b>🏢 Active Centers of Excellence (COEs):</b><br/>• {'<br/>• '.join(role_info['coes'])}<br/><br/>
                        <b>🛠️ Advanced Skill Labs:</b><br/>• {'<br/>• '.join(role_info['skill_labs'])}<br/><br/>
                        <b>🔬 Flagship R&D Projects:</b><br/>• {'<br/>• '.join(role_info['rd_projects'])}<br/><br/>
                        <b>📈 Placement & Salary Stack:</b><br/>{role_info['placement_summary']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            audio_text = role_info.get("audio") or role_info.get("audio_script") or role_info["statement"]
            leader_audio = synthesize_speech_bytes(audio_text)
            if leader_audio:
                st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
                st.caption(f"🎙️ Listen to {role_info['name']}'s Official Audio Address:")
                st.audio(leader_audio, format="audio/mp3")

        with c_l2:
            st.caption("🎥 Leadership & Institutional Vision Address:")
            st.video(role_info["video_url"])


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
