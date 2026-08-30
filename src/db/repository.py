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
    CandidateProfile,
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
    # 1. COLLEGE QUERIES (Safe Dictionary Serialization)
    # =========================================================================

    def get_all_colleges(self) -> List[Dict[str, Any]]:
        """Returns all benchmark colleges as standalone dictionaries."""
        colleges = self.db.query(College).order_by(College.nirf_rank_2025.asc()).all()
        result = []
        for c in colleges:
            result.append({
                "id": str(getattr(c, "id", "")),
                "code": str(getattr(c, "code", "")),
                "name": str(getattr(c, "name", "")),
                "short_name": str(getattr(c, "short_name", "")),
                "state": getattr(c, "state", "Karnataka") or "Karnataka",
                "district": getattr(c, "district", "Bengaluru Urban") or "Bengaluru Urban",
                "city": getattr(c, "city", "Bengaluru") or "Bengaluru",
                "address": getattr(c, "address", "") or "",
                "established_year": getattr(c, "established_year", 1960) or 1960,
                "autonomous": getattr(c, "autonomous", True),
                "naac_grade": getattr(c, "naac_grade", "A") or "A",
                "naac_cgpa": float(getattr(c, "naac_cgpa", 3.0) or 3.0),
                "nba_accredited_programs": int(getattr(c, "nba_accredited_programs", 0) or 0),
                "nirf_rank_2025": getattr(c, "nirf_rank_2025", 100) or 100,
                "intake_total": getattr(c, "intake_total", 1200) or 1200,
                "mgmt_fee_cse_lakhs": float(getattr(c, "mgmt_fee_cse_lakhs", 10.0) or 10.0),
                "govt_fee_cet_lakhs": float(getattr(c, "govt_fee_cet_lakhs", 1.07) or 1.07),
                "comedk_fee_lakhs": float(getattr(c, "comedk_fee_lakhs", 2.81) or 2.81),
                "median_ctc_lpa": float(getattr(c, "median_ctc_lpa", 8.0) or 8.0),
                "highest_ctc_lpa": float(getattr(c, "highest_ctc_lpa", 25.0) or 25.0),
                "departments_and_intake": getattr(c, "departments_and_intake", None),
                "top_recruiters": getattr(c, "top_recruiters", None),
                "coas_and_centers_of_excellence": getattr(c, "coas_and_centers_of_excellence", None),
                "website_link": getattr(c, "website_link", "") or "",
                "video_tour_url": getattr(c, "video_tour_url", "") or "",
                "principal_statement": getattr(c, "principal_statement", "") or "",
                "alumni_linkedin_hub": getattr(c, "alumni_linkedin_hub", "") or "",
            })
        return result

    def get_college_by_code(self, college_code: str) -> Optional[Dict[str, Any]]:
        """Fetches a single college record as a dictionary."""
        if not college_code:
            return None
        c = self.db.query(College).filter(College.code == college_code.upper().strip()).first()
        if not c:
            return None
        return {
            "id": str(getattr(c, "id", "")),
            "code": str(getattr(c, "code", "")),
            "name": str(getattr(c, "name", "")),
            "short_name": str(getattr(c, "short_name", "")),
            "state": getattr(c, "state", "Karnataka") or "Karnataka",
            "district": getattr(c, "district", "Bengaluru Urban") or "Bengaluru Urban",
            "city": getattr(c, "city", "Bengaluru") or "Bengaluru",
            "address": getattr(c, "address", "") or "",
            "established_year": getattr(c, "established_year", 1960) or 1960,
            "autonomous": getattr(c, "autonomous", True),
            "naac_grade": getattr(c, "naac_grade", "A") or "A",
            "naac_cgpa": float(getattr(c, "naac_cgpa", 3.0) or 3.0),
            "nba_accredited_programs": int(getattr(c, "nba_accredited_programs", 0) or 0),
            "nirf_rank_2025": getattr(c, "nirf_rank_2025", 100) or 100,
            "intake_total": getattr(c, "intake_total", 1200) or 1200,
            "mgmt_fee_cse_lakhs": float(getattr(c, "mgmt_fee_cse_lakhs", 10.0) or 10.0),
            "govt_fee_cet_lakhs": float(getattr(c, "govt_fee_cet_lakhs", 1.07) or 1.07),
            "comedk_fee_lakhs": float(getattr(c, "comedk_fee_lakhs", 2.81) or 2.81),
            "median_ctc_lpa": float(getattr(c, "median_ctc_lpa", 8.0) or 8.0),
            "highest_ctc_lpa": float(getattr(c, "highest_ctc_lpa", 25.0) or 25.0),
            "departments_and_intake": getattr(c, "departments_and_intake", None),
            "top_recruiters": getattr(c, "top_recruiters", None),
            "coas_and_centers_of_excellence": getattr(c, "coas_and_centers_of_excellence", None),
            "website_link": getattr(c, "website_link", "") or "",
            "video_tour_url": getattr(c, "video_tour_url", "") or "",
            "principal_statement": getattr(c, "principal_statement", "") or "",
            "alumni_linkedin_hub": getattr(c, "alumni_linkedin_hub", "") or "",
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
        self.db.commit()
        self.db.refresh(reg)
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
        self.db.commit()
        self.db.refresh(school)
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
        self.db.commit()
        self.db.refresh(lead)
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

    # =========================================================================
    # 6. CANDIDATE PROFILER INGESTION & RETRIEVAL
    # =========================================================================

    def save_candidate_profile(self, profile_data: Dict[str, Any]) -> CandidateProfile:
        """Persists candidate multi-test inputs, geographical preferences, and target constraints."""
        profile = CandidateProfile(
            session_id=str(profile_data.get("session_id", "")),
            kcet_rank=int(profile_data.get("kcet_rank", 0) or 0),
            kcet_marks=float(profile_data.get("kcet_marks", 0.0) or 0.0),
            comedk_rank=int(profile_data.get("comedk_rank", 0) or 0),
            comedk_marks=float(profile_data.get("comedk_marks", 0.0) or 0.0),
            jee_percentile=float(profile_data.get("jee_percentile", 0.0) or 0.0),
            pessat_rank=int(profile_data.get("pessat_rank", 0) or 0),
            board_pcm_pct=float(profile_data.get("board_pcm_pct", 0.0) or 0.0),
            preferred_branch=str(profile_data.get("preferred_branch", "CSE") or "CSE"),
            category_quota=str(profile_data.get("category_quota", "GM") or "GM"),
            preferred_city=str(profile_data.get("preferred_city", "All Cities") or "All Cities"),
            preferred_college_type=str(profile_data.get("preferred_college_type", "All Types") or "All Types"),
            seat_quota_pathway=str(profile_data.get("seat_quota_pathway", "Govt Merit Quota (CET)") or "Govt Merit Quota (CET)"),
            max_annual_fee_lakhs=float(profile_data.get("max_annual_fee_lakhs", 15.0) or 15.0),
            min_median_ctc_lpa=float(profile_data.get("min_median_ctc_lpa", 8.0) or 8.0),
            target_highest_ctc_lpa=float(profile_data.get("target_highest_ctc_lpa", 25.0) or 25.0),
            profile_summary_text=str(profile_data.get("profile_summary_text", "") or ""),
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_latest_candidate_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the most recent multi-test profile for a user session."""
        if not session_id:
            return None
        prof = (
            self.db.query(CandidateProfile)
            .filter(CandidateProfile.session_id == session_id)
            .order_by(CandidateProfile.created_at.desc())
            .first()
        )
        if not prof:
            return None
        return {
            "id": prof.id,
            "session_id": prof.session_id,
            "kcet_rank": prof.kcet_rank,
            "kcet_marks": prof.kcet_marks,
            "comedk_rank": prof.comedk_rank,
            "comedk_marks": prof.comedk_marks,
            "jee_percentile": prof.jee_percentile,
            "pessat_rank": prof.pessat_rank,
            "board_pcm_pct": prof.board_pcm_pct,
            "preferred_branch": prof.preferred_branch,
            "category_quota": prof.category_quota,
            "preferred_city": prof.preferred_city,
            "preferred_college_type": prof.preferred_college_type,
            "seat_quota_pathway": prof.seat_quota_pathway,
            "max_annual_fee_lakhs": prof.max_annual_fee_lakhs,
            "min_median_ctc_lpa": prof.min_median_ctc_lpa,
            "target_highest_ctc_lpa": prof.target_highest_ctc_lpa,
            "profile_summary_text": prof.profile_summary_text,
            "created_at": prof.created_at.strftime("%Y-%m-%d %H:%M") if prof.created_at else "—",
        }

    # =========================================================================
    # 7. FACULTY RESEARCH & DEPARTMENT METRICS
    # =========================================================================

    def get_faculty_by_department(
        self, college_code: str, branch_code: str
    ) -> List[Dict[str, Any]]:
        """Retrieves faculty profiles and citations count for a branch as serialized dicts."""
        faculties = (
            self.db.query(Faculty)
            .join(Department, Faculty.dept_id == Department.id)
            .filter(
                Faculty.college_code == college_code.upper(),
                Department.branch_code == branch_code.upper(),
            )
            .order_by(Faculty.citations_count.desc())
            .all()
        )
        return [
            {
                "faculty_id": f.faculty_id,
                "college_code": f.college_code,
                "full_name": f.full_name,
                "designation": f.designation,
                "qualification": f.qualification,
                "research_areas": f.research_areas,
                "google_scholar_url": f.google_scholar_url,
                "linkedin_url": f.linkedin_url,
                "citations_count": f.citations_count,
                "h_index": f.h_index,
                "consulting_projects": f.consulting_projects,
            }
            for f in faculties
        ]
