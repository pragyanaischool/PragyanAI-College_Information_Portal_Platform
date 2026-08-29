"""
tests/test_db_seed.py

Unit tests verifying database ORM models, relational integrity,
cutoff eligibility matching, student search, and lead logging.
"""

from sqlalchemy.orm import Session
from src.db.models import AdmissionLead, College, Cutoff, Student
from src.db.repository import CollegeRepository


def test_college_retrieval(college_repo: CollegeRepository):
    """Verifies retrieval of colleges and summary dataframes."""
    colleges = college_repo.get_all_colleges()
    assert len(colleges) >= 1
    assert colleges[0].code == "E001"
    assert colleges[0].short_name == "RVCE"
    assert colleges[0].naac_grade == "A++"

    df_summary = college_repo.get_colleges_summary_dataframe()
    assert not df_summary.empty
    assert "mgmt_fee_cse_lakhs" in df_summary.columns


def test_cutoff_eligibility_matching(college_repo: CollegeRepository):
    """Verifies rank cutoff filtering for qualified vs disqualified candidates."""
    # Qualified Rank (Rank 3,500 <= Cutoff 4,500)
    df_eligible = college_repo.find_eligible_colleges(
        exam="KCET",
        branch="CSE",
        category="GM",
        student_rank=3500,
        year=2026,
    )
    assert not df_eligible.empty
    assert df_eligible.iloc[0]["college_code"] == "E001"

    # Disqualified Rank (Rank 10,000 > Cutoff 4,500)
    df_ineligible = college_repo.find_eligible_colleges(
        exam="KCET",
        branch="CSE",
        category="GM",
        student_rank=10000,
        year=2026,
    )
    assert df_ineligible.empty


def test_student_talent_search(college_repo: CollegeRepository):
    """Verifies corporate talent querying by skill keyword and CGPA filter."""
    df_talent = college_repo.search_students_by_skills(
        skill_keyword="LangChain",
        min_cgpa=8.0,
        placement_status="Placed",
    )
    assert not df_talent.empty
    assert df_talent.iloc[0]["full_name"] == "Aarav Sharma"
    assert df_talent.iloc[0]["placed_company"] == "Microsoft"


def test_create_admission_lead(college_repo: CollegeRepository, seeded_db_session: Session):
    """Verifies prospective student/parent lead logging and persistence."""
    lead_data = {
        "student_name": "Kavya Ramesh",
        "parent_name": "Ramesh Kulkarni",
        "contact_email": "kavya@gmail.com",
        "contact_phone": "+91 98451 99882",
        "target_college_code": "E001",
        "target_branch": "CSE",
        "admission_type": "Management Quota",
        "intent_score": 5,
        "query_notes": "Interested in direct seat confirmation.",
    }
    lead = college_repo.create_admission_lead(lead_data)
    assert lead.id is not None
    assert lead.intent_score == 5

    df_leads = college_repo.get_admission_leads(college_code="E001")
    assert len(df_leads) >= 1
    assert df_leads.iloc[0]["student_name"] == "Kavya Ramesh"
