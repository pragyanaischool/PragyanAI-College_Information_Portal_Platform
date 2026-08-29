"""
src/db/models.py
SQLAlchemy ORM Data Schema for PragyanAI College Intelligence Hub.
Provides relational mappings for institutional governance, department accreditation,
faculty research profiles, cutoffs, student records, and event management.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class College(Base):
    __tablename__ = "colleges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
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
    top_recruiters = Column(JSON)
    coas_and_centers_of_excellence = Column(JSON)
    video_tour_url = Column(String(500))
    principal_statement = Column(Text)
    alumni_linkedin_hub = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    departments = relationship("Department", back_populates="college", cascade="all, delete-orphan")
    cutoffs = relationship("Cutoff", back_populates="college", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="college", cascade="all, delete-orphan")
    faculties = relationship("Faculty", back_populates="college", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    branch_code = Column(String(20), nullable=False, index=True)  # CSE, AI-DS, ISE, ECE, MECH
    branch_name = Column(String(150), nullable=False)
    hod_name = Column(String(150))
    hod_statement = Column(Text)
    intake = Column(Integer, default=60)
    labs_count = Column(Integer, default=4)
    funded_grants_lakhs = Column(Float, default=0.0)
    patents_filed = Column(Integer, default=0)
    nba_status = Column(String(50), default="Accredited Tier-1")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    college = relationship("College", back_populates="departments")
    faculties = relationship("Faculty", back_populates="department", cascade="all, delete-orphan")


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    faculty_id = Column(String(50), unique=True, nullable=False, index=True)
    college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    dept_id = Column(String(36), ForeignKey("departments.id"), nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    designation = Column(String(100), nullable=False)  # Professor, Associate Prof, Assistant Prof
    qualification = Column(String(100), default="Ph.D.")
    research_areas = Column(Text)
    google_scholar_url = Column(String(500))
    linkedin_url = Column(String(500))
    citations_count = Column(Integer, default=0)
    h_index = Column(Integer, default=0)
    consulting_projects = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    college = relationship("College", back_populates="faculties")
    department = relationship("Department", back_populates="faculties")


class Cutoff(Base):
    __tablename__ = "cutoffs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    college_name = Column(String(255))
    year = Column(Integer, nullable=False, index=True)
    exam = Column(String(20), nullable=False, index=True)  # KCET, COMEDK, JEE-Main
    round_name = Column(String(50), default="Round-2 (Final)")
    branch = Column(String(50), nullable=False, index=True)
    category = Column(String(20), nullable=False, index=True)  # GM, 1G, 2A, 2B, 3A, 3B, SC, ST
    cutoff_rank = Column(Integer, nullable=False, index=True)

    # Relationships
    college = relationship("College", back_populates="cutoffs")


class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_uid = Column(String(50), unique=True, nullable=False, index=True)
    usn = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    college_name = Column(String(255))
    branch = Column(String(50), nullable=False, index=True)
    grad_year = Column(Integer, default=2026, index=True)
    cgpa = Column(Float, nullable=False)
    hackathons_won = Column(Integer, default=0)
    primary_skills = Column(Text)
    placement_status = Column(String(50), nullable=False, index=True)  # Placed, Seeking, Higher Studies
    offered_ctc_lpa = Column(Float, default=0.0)
    placed_company = Column(String(150), default="None", index=True)
    job_title = Column(String(150), default="Student")
    linkedin_url = Column(String(500))
    google_scholar_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    college = relationship("College", back_populates="students")


class OutreachEvent(Base):
    __tablename__ = "outreach_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    track = Column(String(100), nullable=False)  # Deep Tech & AI, Admissions Guidance, Hardware & IoT
    speaker_name = Column(String(150))
    speaker_designation = Column(String(200))
    event_date = Column(String(50))
    event_time = Column(String(50))
    platform = Column(String(100), default="Google Meet / Zoom")
    registration_fee = Column(String(50), default="Free")
    target_audience = Column(String(200))
    brochure_asset = Column(String(500))
    learning_outcomes = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")


class PartnerSchool(Base):
    __tablename__ = "partner_schools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    coordinator_name = Column(String(150))
    coordinator_email = Column(String(150))
    coordinator_phone = Column(String(50))
    registered_batch_size = Column(Integer, default=0)
    selected_program = Column(String(255))
    mou_signed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(50), ForeignKey("outreach_events.event_id"), nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False)
    institution_name = Column(String(255))
    target_exam = Column(String(50))  # KCET, COMEDK, JEE
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("OutreachEvent", back_populates="registrations")


class AdmissionLead(Base):
    __tablename__ = "admission_leads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_name = Column(String(150), nullable=False)
    parent_name = Column(String(150))
    contact_email = Column(String(150), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    target_college_code = Column(String(20), ForeignKey("colleges.code"), nullable=False, index=True)
    target_branch = Column(String(50), nullable=False)
    admission_type = Column(String(50), default="Management Quota")  # Merit, Management Quota, NRI
    entrance_rank = Column(Integer)
    exam_name = Column(String(50))
    intent_score = Column(Integer, default=1)  # 1 (Cold) to 5 (High-Priority Direct Escalation)
    query_notes = Column(Text)
    status = Column(String(50), default="New")  # New, Contacted, Verified, Enrolled
    created_at = Column(DateTime, default=datetime.utcnow)
