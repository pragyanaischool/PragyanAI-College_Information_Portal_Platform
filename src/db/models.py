"""
src/db/models.py

SQLAlchemy ORM Data Schema for PragyanAI College Intelligence Hub.
Provides relational mappings for institutional governance, department accreditation,
faculty research profiles, cutoffs, student records, event management, candidate multi-test profiles,
and published institutional profile records.
"""

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class College(Base):
    __tablename__ = "colleges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), nullable=False)
    state = Column(String(100), default="Karnataka")
    district = Column(String(100), default="Bengaluru Urban")
    city = Column(String(100), nullable=False)
    address = Column(Text)
    established_year = Column(Integer)
    autonomous = Column(Boolean, default=True)
    naac_grade = Column(String(10))
    naac_cgpa = Column(Float)
    nba_accredited_programs = Column(Integer, default=0)
    nirf_rank_2025 = Column(Integer)
    intake_total = Column(Integer)
    mgmt_fee_cse_lakhs = Column(Float)
    govt_fee_cet_lakhs = Column(Float)
    comedk_fee_lakhs = Column(Float)
    median_ctc_lpa = Column(Float)
    highest_ctc_lpa = Column(Float)
    
    # Institutional Governance Fields
    vision = Column(Text, nullable=True, default="Leadership in quality technical education, interdisciplinary research & innovation.")
    mission = Column(Text, nullable=True, default="Deliver outcome-based quality education emphasizing experiential learning and industry collaboration.")

    departments_and_intake = Column(JSON, nullable=True)
    top_recruiters = Column(JSON, nullable=True)
    coas_and_centers_of_excellence = Column(JSON, nullable=True)
    website_link = Column(String(500), nullable=True)
    video_tour_url = Column(String(500), nullable=True)
    principal_statement = Column(Text, nullable=True)
    alumni_linkedin_hub = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    departments = relationship("Department", back_populates="college", cascade="all, delete-orphan")
    cutoffs = relationship("Cutoff", back_populates="college", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="college", cascade="all, delete-orphan")
    faculties = relationship("Faculty", back_populates="college", cascade="all, delete-orphan")
    admission_leads = relationship("AdmissionLead", back_populates="college", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    branch_code = Column(String(20), nullable=False, index=True)  # CSE, AI-DS, ISE, ECE, MECH
    branch_name = Column(String(150), nullable=False)
    hod_name = Column(String(150), nullable=True)
    hod_statement = Column(Text, nullable=True)
    intake = Column(Integer, default=60)
    labs_count = Column(Integer, default=4)
    funded_grants_lakhs = Column(Float, default=0.0)
    patents_filed = Column(Integer, default=0)
    nba_status = Column(String(50), default="Accredited Tier-1")
    
    # Direct JSON Mappings for Departmental Telemetry
    centers_of_excellence = Column(JSON, nullable=True)
    skill_programs = Column(JSON, nullable=True)
    notable_alumni = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    college = relationship("College", back_populates="departments")
    faculties = relationship("Faculty", back_populates="department", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "centers_of_excellence" not in kwargs or not kwargs["centers_of_excellence"]:
            kwargs["centers_of_excellence"] = [
                "AI & High Performance Computing (HPC) Lab",
                "Cloud Native & Distributed Systems Testbed",
                "Autonomous Systems & IoT Innovation Sandbox"
            ]
        if "skill_programs" not in kwargs or not kwargs["skill_programs"]:
            kwargs["skill_programs"] = [
                "Generative AI & LLM Orchestration Bootcamps",
                "Advanced Data Structures & Competitive Programming",
                "Kubernetes & Cloud Infrastructure Automation"
            ]
        if "notable_alumni" not in kwargs or not kwargs["notable_alumni"]:
            kwargs["notable_alumni"] = [
                "Aarav Sharma (Founder, DeepTech AI)",
                "Neha Rao (Principal Engineer, Microsoft)",
                "Vikram Sundaram (Director of Engineering, Google)"
            ]
        super().__init__(**kwargs)


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    faculty_id = Column(String(50), unique=True, nullable=False, index=True)
    college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    dept_id = Column(String(36), ForeignKey("departments.id"), nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    designation = Column(String(100), nullable=False)
    qualification = Column(String(100), default="Ph.D.")
    research_areas = Column(Text, nullable=True)
    google_scholar_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    citations_count = Column(Integer, default=0)
    h_index = Column(Integer, default=0)
    consulting_projects = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    college = relationship("College", back_populates="faculties")
    department = relationship("Department", back_populates="faculties")


class Cutoff(Base):
    __tablename__ = "cutoffs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    college_name = Column(String(255), nullable=True)
    year = Column(Integer, nullable=False, index=True)
    exam = Column(String(20), nullable=False, index=True)
    round_name = Column(String(50), default="Round-2 (Final)")
    branch = Column(String(50), nullable=False, index=True)
    category = Column(String(20), nullable=False, index=True)
    cutoff_rank = Column(Integer, nullable=False, index=True)

    college = relationship("College", back_populates="cutoffs")


class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_uid = Column(String(50), unique=True, nullable=False, index=True)
    usn = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    college_name = Column(String(255), nullable=True)
    branch = Column(String(50), nullable=False, index=True)
    grad_year = Column(Integer, default=2026, index=True)
    cgpa = Column(Float, nullable=False)
    hackathons_won = Column(Integer, default=0)
    primary_skills = Column(Text, nullable=True)
    placement_status = Column(String(50), nullable=False, index=True)
    offered_ctc_lpa = Column(Float, default=0.0)
    placed_company = Column(String(150), default="None", index=True)
    job_title = Column(String(150), default="Student")
    linkedin_url = Column(String(500), nullable=True)
    google_scholar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    college = relationship("College", back_populates="students")


class OutreachEvent(Base):
    __tablename__ = "outreach_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    track = Column(String(100), nullable=False)
    speaker_name = Column(String(150), nullable=True)
    speaker_designation = Column(String(200), nullable=True)
    event_date = Column(String(50), nullable=True)
    event_time = Column(String(50), nullable=True)
    platform = Column(String(100), default="Google Meet / Zoom")
    registration_fee = Column(String(50), default="Free")
    target_audience = Column(String(200), nullable=True)
    brochure_asset = Column(String(500), nullable=True)
    learning_outcomes = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")


class PartnerSchool(Base):
    __tablename__ = "partner_schools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    coordinator_name = Column(String(150), nullable=True)
    coordinator_email = Column(String(150), nullable=True)
    coordinator_phone = Column(String(50), nullable=True)
    registered_batch_size = Column(Integer, default=0)
    selected_program = Column(String(255), nullable=True)
    mou_signed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(50), ForeignKey("outreach_events.event_id"), nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False)
    institution_name = Column(String(255), nullable=True)
    target_exam = Column(String(50), nullable=True)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    event = relationship("OutreachEvent", back_populates="registrations")


class AdmissionLead(Base):
    __tablename__ = "admission_leads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_name = Column(String(150), nullable=False)
    parent_name = Column(String(150), nullable=True)
    contact_email = Column(String(150), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    target_college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    target_branch = Column(String(50), nullable=False)
    admission_type = Column(String(50), default="Management Quota")
    entrance_rank = Column(Integer, nullable=True)
    exam_name = Column(String(50), nullable=True)
    intent_score = Column(Integer, default=1)
    query_notes = Column(Text, nullable=True)
    status = Column(String(50), default="New")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    college = relationship("College", back_populates="admission_leads")


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), index=True, nullable=False)
    kcet_rank = Column(Integer, default=0)
    kcet_marks = Column(Float, default=0.0)
    comedk_rank = Column(Integer, default=0)
    comedk_marks = Column(Float, default=0.0)
    jee_percentile = Column(Float, default=0.0)
    pessat_rank = Column(Integer, default=0)
    board_pcm_pct = Column(Float, default=0.0)
    preferred_branch = Column(String(32), default="CSE")
    category_quota = Column(String(16), default="GM")
    preferred_city = Column(String(64), default="All Cities")
    preferred_college_type = Column(String(64), default="All Types")
    seat_quota_pathway = Column(String(64), default="Govt Merit Quota (CET)")
    max_annual_fee_lakhs = Column(Float, default=15.0)
    min_median_ctc_lpa = Column(Float, default=8.0)
    target_highest_ctc_lpa = Column(Float, default=25.0)
    profile_summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CollegePublishedProfile(Base):
    """Stores complete published institutional profiles, governance details, accreditations, and HOD directories."""
    __tablename__ = "college_published_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    college_code = Column(String(20), unique=True, nullable=False, index=True)
    college_name = Column(String(255), nullable=False)
    city = Column(String(100), default="Bengaluru")
    naac_grade = Column(String(50), default="A++ (CGPA 3.64)")
    nirf_rank = Column(Integer, default=38)
    median_ctc = Column(Float, default=14.5)
    highest_ctc = Column(Float, default=55.0)
    placement_rate = Column(Float, default=96.5)
    
    # Governance & Leadership Statements
    principal_name = Column(String(150), default="Dr. Ramesh Chandra")
    principal_statement = Column(Text, default="Cultivating rigorous technical competency, ethical leadership, and deep-tech research execution.")
    institutional_vision = Column(Text, default="Excellence in autonomous deep-tech research and AI innovation.")
    
    # Department HOD Directories
    hod_cse = Column(String(255), default="Dr. Anand Kumar (Ph.D. IISc)")
    hod_aids = Column(String(255), default="Dr. Sunita Murthy (Ph.D. IITM)")
    hod_ece = Column(String(255), default="Dr. V. K. Hebbar (Ph.D. NITK)")
    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class RecruiterJobPosting(Base):
    """Stores recruiter job descriptions, expressions of interest, and TPO communications."""
    __tablename__ = "recruiter_job_postings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    college_code = Column(String(20), index=True, nullable=False)
    company_name = Column(String(150), nullable=False)
    recruiter_name = Column(String(150), nullable=False)
    recruiter_email = Column(String(150), nullable=False)
    target_role = Column(String(150), nullable=False)
    ctc_range = Column(String(100), nullable=True)
    drive_date = Column(String(50), nullable=True)
    jd_filename = Column(String(255), nullable=True)
    message_to_tpo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


__all__ = [
    "Base",
    "College",
    "Department",
    "Faculty",
    "Cutoff",
    "Student",
    "OutreachEvent",
    "PartnerSchool",
    "EventRegistration",
    "AdmissionLead",
    "CandidateProfile",
    "CollegePublishedProfile",
    "RecruiterJobPosting",
]

