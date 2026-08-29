"""
src/db/repository.py

Data Access and Repository Layer for PragyanAI College Intelligence Hub.
Provides clean query interfaces, aggregations, cutoff feasibility calculations,
lead intake tracking, and talent search methods using SQLAlchemy ORM.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, joinedload

from src.db.models import (
    AdmissionLead,
    College,
    Cutoff,
    Department,
    EventRegistration,
    Faculty,
    OutreachEvent,
    PartnerSchool,
    Student,
)


class CollegeRepository:
  """Unified repository for executing analytical, transactional, and search

  queries across all institutional entities.
  """

  def __init__(self, db: Session):
    self.db = db

  # =========================================================================
  # 1. COLLEGE & INSTITUTIONAL GOVERNANCE QUERIES
  # =========================================================================

  def get_all_colleges(self) -> List[College]:
    """Retrieves all benchmark colleges ordered by NIRF ranking."""
    return self.db.query(College).order_by(College.nirf_rank_2025.asc()).all()

  def get_college_by_code(self, college_code: str) -> Optional[College]:
    """Fetches a single college with full department and faculty relationships loaded."""
    return (
        self.db.query(College)
        .options(
            joinedload(College.departments),
            joinedload(College.faculties),
        )
        .filter(College.code == college_code.upper())
        .first()
    )

  def get_colleges_summary_dataframe(self) -> pd.DataFrame:
    """Returns a pandas DataFrame of all colleges for ROI analysis and chart rendering."""
    query = self.db.query(
        College.code,
        College.name,
        College.short_name,
        College.city,
        College.naac_grade,
        College.naac_cgpa,
        College.nirf_rank_2025,
        College.mgmt_fee_cse_lakhs,
        College.govt_fee_cet_lakhs,
        College.comedk_fee_lakhs,
        College.median_ctc_lpa,
        College.highest_ctc_lpa,
    )
    return pd.read_sql(query.statement, self.db.bind)

  # =========================================================================
  # 2. CUTOFFS, ADMISSION FEASIBILITY & PREDICTION
  # =========================================================================

  def find_eligible_colleges(
      self,
      exam: str,
      branch: str,
      category: str,
      student_rank: int,
      year: int = 2026,
      limit: int = 10,
  ) -> pd.DataFrame:
    """Calculates admission eligibility based on entrance rank, exam, and category."""
    query = (
        self.db.query(
            College.name.label("college_name"),
            College.code.label("college_code"),
            College.city,
            College.naac_grade,
            College.nirf_rank_2025,
            Cutoff.branch,
            Cutoff.cutoff_rank,
            College.mgmt_fee_cse_lakhs.label("mgmt_fee_lpa"),
            College.median_ctc_lpa,
            College.highest_ctc_lpa,
        )
        .join(Cutoff, College.code == Cutoff.college_code)
        .filter(
            Cutoff.exam == exam.upper(),
            Cutoff.branch == branch.upper(),
            Cutoff.category == category.upper(),
            Cutoff.year == year,
            Cutoff.cutoff_rank >= student_rank,
        )
        .order_by(Cutoff.cutoff_rank.asc())
        .limit(limit)
    )
    return pd.read_sql(query.statement, self.db.bind)

  def get_cutoff_trends(
      self, college_code: str, branch: str, exam: str = "KCET"
  ) -> pd.DataFrame:
    """Retrieves 3-year historical cutoff trends for a specific branch and college."""
    query = (
        self.db.query(
            Cutoff.year,
            Cutoff.category,
            Cutoff.cutoff_rank,
            Cutoff.round_name,
        )
        .filter(
            Cutoff.college_code == college_code.upper(),
            Cutoff.branch == branch.upper(),
            Cutoff.exam == exam.upper(),
        )
        .order_by(Cutoff.year.asc(), Cutoff.category.asc())
    )
    return pd.read_sql(query.statement, self.db.bind)

  # =========================================================================
  # 3. STUDENT TALENT, SKILLS & PLACEMENT SEARCH
  # =========================================================================

  def search_students_by_skills(
      self,
      skill_keyword: str,
      min_cgpa: float = 0.0,
      placement_status: Optional[str] = None,
      limit: int = 200,
  ) -> pd.DataFrame:
    """Enables corporate recruiters to query verified talent by technical competencies."""
    filters = [Student.cgpa >= min_cgpa]

    if skill_keyword and skill_keyword.lower() != "all":
      filters.append(Student.primary_skills.ilike(f"%{skill_keyword}%"))

    if placement_status and placement_status.lower() != "all":
      filters.append(Student.placement_status == placement_status)

    query = (
        self.db.query(
            Student.usn,
            Student.full_name,
            Student.college_name,
            Student.branch,
            Student.cgpa,
            Student.hackathons_won,
            Student.primary_skills,
            Student.placement_status,
            Student.offered_ctc_lpa,
            Student.placed_company,
            Student.linkedin_url,
        )
        .filter(*filters)
        .order_by(Student.cgpa.desc())
        .limit(limit)
    )
    return pd.read_sql(query.statement, self.db.bind)

  def get_placement_metrics(self) -> Dict[str, Any]:
    """Aggregates overall placement and salary benchmarks across 1,000+ students."""
    total_students = self.db.query(func.count(Student.id)).scalar() or 0
    placed_students = (
        self.db.query(func.count(Student.id))
        .filter(Student.placement_status == "Placed")
        .scalar()
        or 0
    )
    avg_placed_ctc = (
        self.db.query(func.avg(Student.offered_ctc_lpa))
        .filter(Student.placement_status == "Placed")
        .scalar()
        or 0.0
    )
    highest_placed_ctc = (
        self.db.query(func.max(Student.offered_ctc_lpa)).scalar() or 0.0
    )

    return {
        "total_students": total_students,
        "placed_students": placed_students,
        "placement_rate_pct": round(
            (placed_students / total_students * 100)
            if total_students > 0
            else 0.0,
            2,
        ),
        "average_ctc_lpa": round(avg_placed_ctc, 2),
        "highest_ctc_lpa": round(highest_placed_ctc, 2),
    }

  # =========================================================================
  # 4. OUTREACH, WEBINARS & SCHOOL PARTNERSHIP MANAGEMENT
  # =========================================================================

  def get_active_outreach_events(self) -> List[OutreachEvent]:
    """Fetches upcoming masterclasses, free bootcamps, and admissions webinars."""
    return (
        self.db.query(OutreachEvent)
        .order_by(OutreachEvent.event_date.asc())
        .all()
    )

  def register_student_for_event(self, registration_data: Dict[str, Any]) -> EventRegistration:
    """Registers an individual student/aspirant for an outreach event."""
    reg = EventRegistration(
        event_id=registration_data["event_id"],
        full_name=registration_data["full_name"],
        email=registration_data["email"],
        phone=registration_data["phone"],
        institution_name=registration_data.get("institution_name", ""),
        target_exam=registration_data.get("target_exam", "KCET"),
    )
    self.db.add(reg)
    self.db.commit()
    self.db.refresh(reg)
    return reg

  def register_partner_school(self, school_data: Dict[str, Any]) -> PartnerSchool:
    """Enrolls a high school or PU college for bulk bootcamp cohorts."""
    school = PartnerSchool(
        school_name=school_data["school_name"],
        city=school_data["city"],
        coordinator_name=school_data.get("coordinator_name", ""),
        coordinator_email=school_data.get("coordinator_email", ""),
        coordinator_phone=school_data.get("coordinator_phone", ""),
        registered_batch_size=school_data.get("registered_batch_size", 0),
        selected_program=school_data.get("selected_program", ""),
        mou_signed=school_data.get("mou_signed", False),
    )
    self.db.add(school)
    self.db.commit()
    self.db.refresh(school)
    return school

  def get_all_partner_schools(self) -> List[PartnerSchool]:
    """Retrieves all registered partner feeder institutions."""
    return (
        self.db.query(PartnerSchool)
        .order_by(PartnerSchool.created_at.desc())
        .all()
    )

  # =========================================================================
  # 5. ADMISSIONS CRM & HIGH-INTENT LEAD PIPELINE
  # =========================================================================

  def create_admission_lead(self, lead_data: Dict[str, Any]) -> AdmissionLead:
    """Logs a prospective parent/student lead with automatic intent priority score."""
    lead = AdmissionLead(
        student_name=lead_data["student_name"],
        parent_name=lead_data.get("parent_name", ""),
        contact_email=lead_data["contact_email"],
        contact_phone=lead_data["contact_phone"],
        target_college_code=lead_data["target_college_code"],
        target_branch=lead_data["target_branch"],
        admission_type=lead_data.get("admission_type", "Management Quota"),
        entrance_rank=lead_data.get("entrance_rank"),
        exam_name=lead_data.get("exam_name", "KCET"),
        intent_score=lead_data.get("intent_score", 3),
        query_notes=lead_data.get("query_notes", ""),
        status="New",
    )
    self.db.add(lead)
    self.db.commit()
    self.db.refresh(lead)
    return lead

  def get_admission_leads(
      self, college_code: Optional[str] = None
  ) -> pd.DataFrame:
    """Pulls all admission inquiries formatted for the leadership CRM view."""
    query = self.db.query(
        AdmissionLead.student_name,
        AdmissionLead.parent_name,
        AdmissionLead.contact_email,
        AdmissionLead.contact_phone,
        AdmissionLead.target_college_code,
        AdmissionLead.target_branch,
        AdmissionLead.admission_type,
        AdmissionLead.entrance_rank,
        AdmissionLead.intent_score,
        AdmissionLead.status,
        AdmissionLead.created_at,
    )
    if college_code:
      query = query.filter(
          AdmissionLead.target_college_code == college_code.upper()
      )

    query = query.order_by(
        AdmissionLead.intent_score.desc(), AdmissionLead.created_at.desc()
    )
    return pd.read_sql(query.statement, self.db.bind)

  # =========================================================================
  # 6. FACULTY RESEARCH & DEPARTMENT METRICS
  # =========================================================================

  def get_faculty_by_department(
      self, college_code: str, branch_code: str
  ) -> List[Faculty]:
    """Retrieves faculty profiles and Google Scholar citation indices for a branch."""
    return (
        self.db.query(Faculty)
        .join(Department, Faculty.dept_id == Department.id)
        .filter(
            Faculty.college_code == college_code.upper(),
            Department.branch_code == branch_code.upper(),
        )
        .order_by(Faculty.citations_count.desc())
        .all()
    )
