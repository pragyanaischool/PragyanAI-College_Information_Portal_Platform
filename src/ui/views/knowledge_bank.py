"""
src/ui/views/knowledge_bank.py

Dedicated Knowledge Bank & Engineering College Selection Guide:
Provides deep-dive explanations on statutory accreditations (NAAC, NBA, NIRF), 
classification types (University, Autonomous, Affiliated), and the vital evaluation 
framework required for choosing an engineering college.
"""

import streamlit as st


def render_knowledge_bank_view():
    """Renders the comprehensive Knowledge Bank, college classification glossary, and selection strategy guide."""
    st.title(" PragyanAI - Aspirant Knowledge Bank & College Selection Guide")
    st.markdown(
        "Empowering engineering aspirants and parents with crystal-clear insights into statutory accreditations, "
        "national rankings, institutional classifications, and the critical evaluation framework needed to make an informed choice."
    )
    st.markdown("---")

    # Navigation Sub-tabs for the Knowledge Bank
    t_types, t_accred, t_pillars = st.tabs([
        "1. Institution Classifications & Glossary",
        "2. Decoding NBA, NAAC & NIRF Rankings",
        "3. Key Criteria for Selecting an Engineering College"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Institution Classifications & Glossary
    # -------------------------------------------------------------------------
    with t_types:
        st.subheader("📖 Glossary: Understanding University, Autonomous, and Affiliated Colleges")
        st.markdown(
            """
            When choosing an engineering college, understanding how academic governance, curriculum control, and degree certification work is vital:

            -  **University (Deemed / State / Private):** 
              Universities possess statutory authority to design their own curriculums, conduct examinations, and award degrees directly under their own seal. They often span multiple faculties, governing bodies, and advanced research centers.
            
            -  **Autonomous Colleges:** 
              These institutions are affiliated with a parent university (e.g., Visvesvaraya Technological University - VTU) but are granted formal academic freedom by the UGC. They design their own updated syllabi, conduct internal assessments, and grade students independently, allowing for much faster curriculum modernization (e.g., introducing Artificial Intelligence, Agentic Workflows, and GenAI tracks rapidly).
            
            -  **University Affiliated (Non-Autonomous):** 
              Colleges that strictly follow the rigid curriculum, exam schedules, and evaluation guidelines prescribed by the central affiliating university. Curriculum revisions in these institutions typically follow slow central university cycles.
            """
        )

    # -------------------------------------------------------------------------
    # TAB 2: Decoding NBA, NAAC & NIRF
    # -------------------------------------------------------------------------
    with t_accred:
        st.subheader("🎖️ What Do College Accreditations and National Rankings Mean?")
        st.markdown(
            """
            Institutional accreditations and rankings are third-party quality audits that protect students from substandard education:

            - 1. **NAAC Accreditation (National Assessment and Accreditation Council):**
              * *Scope:* Evaluates the **overall institution/university** across governance, faculty-student ratios, infrastructure, library systems, and student welfare.
              * *Grading Scale:* Renders grades ranging from **A++** (highest CGPA 3.51 - 4.00) down to A+, A, B, and C.
              * *Why it matters:* High NAAC ratings guarantee institutional stability and are heavily scrutinized by foreign universities for master’s degree (MS/M.Tech) admissions.

            - 2. **NBA Accreditation (National Board of Accreditation):**
              * *Scope:* Unlike NAAC, NBA evaluates **specific engineering programs and departments** (e.g., B.E. in Computer Science, ECE, Mechanical) based on outcome-based education (OBE).
              * *Tier-1 Status:* NBA Tier-1 accredited programs fall under the international **Washington Accord**, meaning your engineering degree is legally recognized across member nations (US, UK, Canada, Australia, Japan, Germany) without requiring bridge examinations.

            - 3. **NIRF Ranking (National Institutional Ranking Framework):**
              * *Scope:* Published annually by the Ministry of Education, Government of India.
              * *Parameters:* Measures institutions across Teaching & Learning Resources (TLR), Research Productivity & Patents (RP), Graduation Outcomes (Placement percentage and Median CTC), Outreach, and Peer Perception.
            """
        )

    # -------------------------------------------------------------------------
    # TAB 3: Key Criteria for Selecting a College
    # -------------------------------------------------------------------------
    with t_pillars:
        st.subheader("🔍 Key Points One Needs to Look When Selecting an Engineering College")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("#### 1. Placement ROI & CTC Packages")
            st.write("Look beyond peak marketing packages. Analyze median CTC figures in your target branch, placement percentage consistency, and whether recruiting companies are core technical product firms or volume-based service companies.")

            st.markdown("#### 2. Curriculum Agility & Skill Tracks")
            st.write("Check if the institution embeds practical tech stacks (Cloud computing, Full-Stack, VLSI, and AI tools) directly into coursework rather than relying solely on legacy theory.")

            st.markdown("#### 3. Key Faculty Profiles & Credentials")
            st.write("Examine faculty qualifications (percentage of Ph.D. holders from IITs/IISc), Google Scholar citation counts, and active industry consulting projects.")

            st.markdown("#### 4. Infrastructure & Computing Labs")
            st.write("Inspect physical laboratory setups, high-compute GPU/cloud access for AI workloads, library resources, and active maker spaces.")

        with col_p2:
            st.markdown("#### 5. Centers of Excellence (COEs)")
            st.write("Verify institutional partnerships with global tech leaders (NVIDIA, Intel, AWS, Cisco, Bosch) that sponsor specialized training infrastructure on campus.")

            st.markdown("#### 6. Alumni Network Status & Mentorship")
            st.write("An active alumni network working in senior engineering roles at top product companies provides invaluable mentorship, internship referrals, and career navigation.")

            st.markdown("#### 7. Total Cost & Financial Payback Period")
            st.write("Calculate your total 4-year financial investment (tuition fees under CET, COMEDK, or Management quotas) against starting median salaries. An ideal educational ROI payback period should be under 24 months.")


if __name__ == "__main__":
    render_knowledge_bank_view()
