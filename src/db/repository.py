"""
src/db/repository.py

Data Access and Repository Layer for PragyanAI College Intelligence Hub.
Provides query interfaces returning plain dictionaries and DataFrames to avoid
detached instance errors across Streamlit session runs.
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
    """Unified repository for analytical and transactional database operations."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # 1. COLLEGE QUERIES
    # =========================================================================

    def get_all_colleges(self) -> List[Dict[str, Any]]:
        """Returns all benchmark colleges as standalone dictionaries."""
        colleges = self.db.query(College).order_by(College.nirf_rank_2025.asc()).all()
        return [
            {
                "code": c.code,
                "name": c.name,
                "short_name": c.short_name,
                "city": c.city,
                "established_year": c.established_year,
                "autonomous": c.autonomous,
                "naac_grade": c.naac_grade,
                "naac_cgpa": c.naac_cgpa,
                "nba_accredited_programs": c.nba_accredited_programs,
                "nirf_rank_2025": c.nirf_rank_2025,
                "mgmt_fee_cse_lakhs": c.mgmt_fee_cse_lakhs,
                "govt_fee_cet_lakhs": c.govt_fee_cet_lakhs,
                "comedk_fee_lakhs": c.comedk_fee_lakhs,
                "median_ctc_lpa": c.median_ctc_lpa,
                "highest_ctc_lpa": c.highest_ctc_lpa,
            }
            for c in colleges
        ]

    def get_college_by_code(self, college_code: str) -> Optional[Dict[str, Any]]:
        """Fetches a single college record as a dictionary."""
        c = self.db.query(College).filter(College.code == college_code.upper()).first()
        if not c:
            return None
        return {
            "code": c.code,
            "name": c.name,
            "short_name": c.short_name,
            "city": c.city,
            "established_year": c.established_year,
            "autonomous": c.autonomous,
            "naac_grade": c.naac_grade,
            "naac_cgpa": c.naac_cgpa,
            "nba_accredited_programs": c.nba_accredited_programs,
            "nirf_rank_2025": c.nirf_rank_2025,
            "mgmt_fee_cse_lakhs": c.mgmt_fee_cse_lakhs,
            "govt_fee_cet_lakhs": c.govt_fee_cet_lakhs,
            "comedk_fee_lakhs": c.comedk_fee_lakhs,
            "median_ctc_lpa": c.median_ctc_lpa,
            "highest_ctc_lpa": c.highest_ctc_lpa,
        }

    def get_colleges_summary_dataframe(self) -> pd.DataFrame:
        """Returns a pandas DataFrame of benchmark colleges."""
        colleges = self.get_all_colleges()
        return pd.DataFrame(colleges)

    # =========================================================================
    # 2. CUTOFFS & ADMISSION FEASIBILITY
    # =========================================================================

    def find_eligible_colleges(
        self,
        exam: str,
        branch: str,
        category: str,
        student_rank: int,
        year: int = 2026,
        limit: int = 20,
    ) -> pd.DataFrame:
        """Calculates admission eligibility based on entrance rank."""
        query = (
            self.db.query(
                College.name.label("college_name"),
                College.code.label("college_code"),
                College.city,
                College.naac_grade,
                College.naac_cgpa,
                College.nirf_rank_2025,
                Cutoff.branch,
                Cutoff.cutoff_rank,
                College.mgmt_fee_cse_lakhs.label("mgmt_fee_lpa"),
                College.mgmt_fee_cse_lakhs.label("mgmt_fee_cse_lakhs"),
                College.median_ctc_lpa,
                College.highest_ctc_lpa,
            )
            .join(Cutoff, College.code == Cutoff.college_code)
            .filter(
                Cutoff.exam == exam.upper(),
                Cutoff.branch == branch.upper(),
                Cutoff.category == category.upper(),
                Cutoff.year == int(year),
                Cutoff.cutoff_rank >= int(student_rank * 0.85),
            )
            .order_by(Cutoff.cutoff_rank.asc())
            .limit(limit)
        )

        results = query.all()
        if not results:
            return pd.DataFrame()

        records = [
            {
                "college_code": r.college_code,
                "college_name": r.college_name,
                "city": r.city,
                "branch": r.branch,
                "cutoff_rank": r.cutoff_rank,
                "naac_grade": r.naac_grade,
                "naac_cgpa": r.naac_cgpa,
                "nirf_rank_2025": r.nirf_rank_2025,
                "mgmt_fee_lpa": r.mgmt_fee_lpa,
                "mgmt_fee_cse_lakhs": r.mgmt_fee_cse_lakhs,
                "median_ctc_lpa": r.median_ctc_lpa,
                "highest_ctc_lpa": r.highest_ctc_lpa,
            }
            for r in results
        ]
        return pd.DataFrame(records)

    def get_cutoff_trends(
        self, college_code: str, branch: str, exam: str = "KCET"
    ) -> pd.DataFrame:
        """Retrieves historical cutoff trends."""
        cutoffs = (
            self.db.query(Cutoff)
            .filter(
                Cutoff.college_code == college_code.upper(),
                Cutoff.branch == branch.upper(),
                Cutoff.exam == exam.upper(),
            )
            .order_by(Cutoff.year.asc(), Cutoff.category.asc())
            .all()
        )
        records = [
            {
                "year": c.year,
                "category": c.category,
                "cutoff_rank": c.cutoff_rank,
                "round_name": c.round_name,
            }
            for c in cutoffs
        ]
        return pd.DataFrame(records)

    # =========================================================================
    # 3. STUDENT TALENT & PLACEMENTS
    # =========================================================================

    def filter_students(
        self,
        min_cgpa: float = 0.0,
        skill_query: Optional[str] = None,
        branch: Optional[str] = None,
        placement_status: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Filters student profiles based on recruiter search parameters."""
        query = self.db.query(Student).filter(Student.cgpa >= min_cgpa)

        if branch and branch != "All Branches":
            query = query.filter(Student.branch == branch.upper())
        if placement_status and placement_status != "All Statuses":
            query = query.filter(Student.placement_status == placement_status)
        if skill_query and skill_query.strip():
            query = query.filter(Student.primary_skills.ilike(f"%{skill_query.strip()}%"))

        students = query.order_by(Student.cgpa.desc()).limit(limit).all()

        records = [
            {
                "student_uid": s.student_uid or s.usn,
                "usn": s.usn,
                "full_name": s.full_name,
                "college_name": s.college_name,
                "branch": s.branch,
                "cgpa": s.cgpa,
                "hackathons_won": s.hackathons_won,
                "primary_skills": s.primary_skills,
                "placement_status": s.placement_status,
                "offered_ctc_lpa": s.offered_ctc_lpa,
                "placed_company": s.placed_company or "—",
                "job_title": s.job_title or "—",
                "linkedin_url": s.linkedin_url,
            }
            for s in students
        ]
        return pd.DataFrame(records)

    def search_students_by_skills(
        self,
        skill_keyword: str,
        min_cgpa: float = 0.0,
        placement_status: Optional[str] = None,
        limit: int = 200,
    ) -> pd.DataFrame:
        """Alias helper for skill-based talent querying."""
        return self.filter_students(
            min_cgpa=min_cgpa,
            skill_query=skill_keyword,
            branch=None,
            placement_status=placement_status,
            limit=limit,
        )

    def get_placement_metrics(self) -> Dict[str, Any]:
        """Aggregates placement and salary benchmarks."""
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
                (placed_students / total_students * 100) if total_students > 0 else 0.0,
                2,
            ),
            "average_ctc_lpa": round(avg_placed_ctc, 2),
            "highest_ctc_lpa": round(highest_placed_ctc, 2),
        }

    # =========================================================================
    # 4. OUTREACH & WEBINARS
    # =========================================================================

    def get_outreach_events(self) -> List[Dict[str, Any]]:
        """Returns all scheduled events as dictionaries."""
        events = self.db.query(OutreachEvent).order_by(OutreachEvent.event_date.asc()).all()
        return [
            {
                "event_id": e.event_id,
                "title": e.title,
                "track": e.track,
                "speaker_name": e.speaker_name,
                "speaker_designation": e.speaker_designation,
                "event_date": e.event_date,
                "event_time": e.event_time,
                "platform": e.platform,
                "registration_fee": e.registration_fee,
                "target_audience": e.target_audience,
                "learning_outcomes": e.learning_outcomes,
                "stream_url": getattr(e, "stream_url", None),
            }
            for e in events
        ]

    def register_student_for_event(self, registration_data: Dict[str, Any]) -> EventRegistration:
        """Registers a student for an outreach event."""
        reg = EventRegistration(
            event_id=registration_data["event_id"],
            full_name=registration_data["full_name"],
            email=registration_data["email"],
            phone=registration_data["phone"],
            institution_name=registration_data.get("institution_name", ""),
            target_exam=registration_data.get("target_exam", "KCET"),
        )
        self.db.add(reg)
        self.db.flush()
        return reg

    def register_partner_school(self, school_data: Dict[str, Any]) -> PartnerSchool:
        """Registers a partner school for cohort training."""
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
        self.db.flush()
        return school

    def register_school_partner(self, partner_data: Dict[str, Any]) -> PartnerSchool:
        """Alias for register_partner_school."""
        return self.register_partner_school(partner_data)

    # =========================================================================
    # 5. ADMISSIONS CRM LEADS
    # =========================================================================

    def create_admission_lead(self, lead_data: Dict[str, Any]) -> AdmissionLead:
        """Logs an admission inquiry."""
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
            status=lead_data.get("status", "New"),
        )
        self.db.add(lead)
        self.db.flush()
        return lead

    def get_admission_leads(
        self, college_code: Optional[str] = None, limit: int = 100
    ) -> pd.DataFrame:
        """Fetches admission leads for CRM monitoring."""
        query = self.db.query(AdmissionLead)
        if college_code:
            query = query.filter(AdmissionLead.target_college_code == college_code.upper())

        leads = query.order_by(AdmissionLead.intent_score.desc(), AdmissionLead.created_at.desc()).limit(limit).all()

        records = [
            {
                "id": l.id,
                "student_name": l.student_name,
                "parent_name": l.parent_name or "—",
                "contact_email": l.contact_email,
                "contact_phone": l.contact_phone,
                "target_college_code": l.target_college_code,
                "target_branch": l.target_branch,
                "admission_type": l.admission_type,
                "entrance_rank": l.entrance_rank or "—",
                "intent_score": l.intent_score,
                "status": l.status,
                "created_at": l.created_at.strftime("%Y-%m-%d %H:%M") if l.created_at else "—",
            }
            for l in leads
        ]
        return pd.DataFrame(records)
