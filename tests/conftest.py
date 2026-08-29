"""
tests/conftest.py

Shared pytest fixtures providing an isolated in-memory SQLite database,
pre-seeded benchmark test tables, and mock LLM configurations.
"""

import os
from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings
from src.db.models import Base, College, Cutoff, Department, OutreachEvent, Student
from src.db.repository import CollegeRepository

# Use an in-memory SQLite engine for fast, isolated test execution
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """Creates a shared in-memory SQLite engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Provides a transactional database session per test function with automated rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def seeded_db_session(db_session: Session) -> Session:
    """Pre-populates sample test data for colleges, cutoffs, students, and events."""
    # 1. Insert College
    college = College(
        code="E001",
        name="RV College of Engineering",
        short_name="RVCE",
        city="Bengaluru",
        naac_grade="A++",
        naac_cgpa=3.78,
        nirf_rank_2025=89,
        mgmt_fee_cse_lakhs=16.0,
        govt_fee_cet_lakhs=1.07,
        comedk_fee_lakhs=2.81,
        median_ctc_lpa=14.5,
        highest_ctc_lpa=62.0,
        top_recruiters=["Microsoft", "Amazon", "Cisco"],
        coas_and_centers_of_excellence=["Center of Excellence in Quantum Computing & AI"],
    )
    db_session.add(college)

    # 2. Insert Cutoff
    cutoff = Cutoff(
        college_code="E001",
        college_name="RV College of Engineering",
        year=2026,
        exam="KCET",
        round_name="Round-2 (Final)",
        branch="CSE",
        category="GM",
        cutoff_rank=4500,
    )
    db_session.add(cutoff)

    # 3. Insert Student
    student = Student(
        student_uid="std-00001",
        usn="1RV22CS0001",
        full_name="Aarav Sharma",
        college_code="E001",
        college_name="RV College of Engineering",
        branch="CSE",
        cgpa=9.45,
        hackathons_won=2,
        primary_skills="PyTorch, LangChain, FastAPI, Docker",
        placement_status="Placed",
        offered_ctc_lpa=32.0,
        placed_company="Microsoft",
        job_title="AI / Systems Engineer",
    )
    db_session.add(student)

    # 4. Insert Outreach Event
    event = OutreachEvent(
        event_id="evt-001",
        title="Masterclass: Generative AI, RAG & Agentic AI using LangGraph",
        track="Deep Tech & AI",
        speaker_name="Sateesh Ambesange",
        speaker_designation="Founder & AI Architect, PragyanAI",
        event_date="2026-09-05",
        event_time="11:00 AM - 1:00 PM IST",
        platform="Google Meet / YouTube Live",
        registration_fee="Free",
        target_audience="PU College & High School Seniors",
    )
    db_session.add(event)

    db_session.commit()
    return db_session


@pytest.fixture(scope="function")
def college_repo(seeded_db_session: Session) -> CollegeRepository:
    """Returns an initialized repository instance wired to the seeded test database."""
    return CollegeRepository(seeded_db_session)
