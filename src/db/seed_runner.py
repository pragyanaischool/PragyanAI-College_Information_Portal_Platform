"""
src/db/seed_runner.py

Database Initialization and Data Ingestion Pipeline for PragyanAI College Intelligence Hub.
Reads generated datasets from 'data/seed/' and populates relational database tables
(Colleges, Departments, Faculties, Cutoffs, Students, OutreachEvents, PartnerSchools, AdmissionLeads)
using SQLAlchemy ORM models defined in src.db.models.
"""

import json
import os
import random
import uuid
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.models import (
    AdmissionLead,
    Base,
    College,
    Cutoff,
    Department,
    EventRegistration,
    Faculty,
    OutreachEvent,
    PartnerSchool,
    Student,
)

# Configuration & Paths
DB_PATH = "data/college_portal.db"
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

SEED_COLLEGES = "data/seed/colleges.json"
SEED_CUTOFFS = "data/seed/cutoffs.csv"
SEED_STUDENTS = "data/seed/students_synthetic.csv"
SEED_EVENTS = "data/seed/outreach_events.json"


def seed_database(db_url: str = DB_URL):
  """Initializes the database schema and ingests seed datasets."""
  os.makedirs("data", exist_ok=True)
  print(f"[*] Connecting to database at: {db_url}")

  engine = create_engine(db_url, echo=False)

  # Recreate tables
  print("[*] Rebuilding database schema...")
  Base.metadata.drop_all(engine)
  Base.metadata.create_all(engine)

  SessionLocal = sessionmaker(bind=engine)
  session = SessionLocal()

  try:
    # =========================================================================
    # 1. SEED COLLEGES, DEPARTMENTS & FACULTIES
    # =========================================================================
    if os.path.exists(SEED_COLLEGES):
      print(f"[*] Ingesting colleges and departments from {SEED_COLLEGES}...")
      with open(SEED_COLLEGES, "r", encoding="utf-8") as f:
        colleges_raw = json.load(f)

      dept_templates = [
          (
              "CSE",
              "Computer Science & Engineering",
              240,
              8,
              55.0,
              14,
              "Dr. Anand V. Kulkarni",
              "Ph.D. (IISc)",
              "Generative AI, Distributed Systems, Large Language Models",
          ),
          (
              "AI-DS",
              "Artificial Intelligence & Data Science",
              120,
              5,
              45.0,
              10,
              "Dr. Meenakshi Sundaram",
              "Ph.D. (IIT Madras)",
              "Agentic AI, Computer Vision, Deep Learning, MLOps",
          ),
          (
              "ISE",
              "Information Science & Engineering",
              180,
              6,
              35.0,
              8,
              "Dr. Rajeshwari Hegde",
              "Ph.D. (NITK)",
              "Cloud Architecture, Cyber-Physical Systems, Data Engineering",
          ),
          (
              "ECE",
              "Electronics & Communication Engineering",
              180,
              7,
              50.0,
              12,
              "Dr. Sudhir Rao",
              "Ph.D. (IIT Bombay)",
              "VLSI Architecture, RTL Verification, Embedded RTOS, 5G/6G",
          ),
          (
              "MECH",
              "Mechanical Engineering",
              120,
              6,
              30.0,
              6,
              "Dr. P. C. Shettar",
              "Ph.D. (IIT Kharagpur)",
              "Autonomous Robotics, Computational Fluid Dynamics, Smart Materials",
          ),
      ]

      for c in colleges_raw:
        college = College(
            id=c.get("college_id", str(uuid.uuid4())),
            code=c["code"],
            name=c["name"],
            short_name=c["short_name"],
            city=c["city"],
            established_year=c.get("established_year", 1980),
            autonomous=c.get("autonomous", True),
            naac_grade=c.get("naac_grade", "A"),
            naac_cgpa=c.get("naac_cgpa", 3.2),
            nba_accredited_programs=c.get("nba_accredited_programs", 6),
            nirf_rank_2025=c.get("nirf_rank_2025", 150),
            intake_total=c.get("intake_total", 1200),
            mgmt_fee_cse_lakhs=c.get("mgmt_fee_cse_lakhs", 7.0),
            govt_fee_cet_lakhs=c.get("govt_fee_cet_lakhs", 1.07),
            comedk_fee_lakhs=c.get("comedk_fee_lakhs", 2.81),
            median_ctc_lpa=c.get("median_ctc_lpa", 8.0),
            highest_ctc_lpa=c.get("highest_ctc_lpa", 35.0),
            top_recruiters=c.get("top_recruiters", []),
            coas_and_centers_of_excellence=c.get(
                "coas_and_centers_of_excellence", []
            ),
            video_tour_url=c.get("video_tour_url", ""),
            principal_statement=c.get("principal_statement", ""),
            alumni_linkedin_hub=c.get("alumni_linkedin_hub", ""),
        )
        session.add(college)
        session.flush()  # Ensures college is present for foreign key references

        # Populate Academic Departments & Faculty Researchers
        for (
            b_code,
            b_name,
            b_intake,
            labs,
            grants,
            patents,
            hod_name,
            hod_qual,
            research_areas,
        ) in dept_templates:
          dept_uuid = str(uuid.uuid4())
          dept = Department(
              id=dept_uuid,
              college_code=c["code"],
              branch_code=b_code,
              branch_name=b_name,
              hod_name=hod_name,
              hod_statement=(
                  f"Driving state-of-the-art innovation, Tier-1 NBA excellence,"
                  f" and multidisciplinary research in {b_name}."
              ),
              intake=b_intake,
              labs_count=labs,
              funded_grants_lakhs=grants,
              patents_filed=patents,
              nba_status="Accredited Tier-1 (Valid up to 2028)",
          )
          session.add(dept)

          # Add HOD / Lead Faculty Profile with research metrics
          faculty = Faculty(
              faculty_id=f"FAC-{c['code']}-{b_code}-01",
              college_code=c["code"],
              dept_id=dept_uuid,
              full_name=hod_name,
              designation="Professor & Head of Department",
              qualification=hod_qual,
              research_areas=research_areas,
              google_scholar_url=f"https://scholar.google.com/citations?user={c['code'].lower()}_{b_code.lower()}_01",
              linkedin_url=f"https://www.linkedin.com/in/{hod_name.lower().replace(' ', '-').replace('.', '')}/",
              citations_count=random.randint(450, 2800),
              h_index=random.randint(12, 28),
              consulting_projects=[
                  {
                      "client": "Samsung R&D / Bosch / DST",
                      "title": f"Applied {b_code} Industrial Optimization Suite",
                      "grant_lakhs": round(random.uniform(8.0, 25.0), 1),
                  }
              ],
          )
          session.add(faculty)

      session.commit()
      print(
          f"  [+] Ingested {len(colleges_raw)} Colleges, 75 Academic"
          " Departments & Faculty Researchers."
      )

    # =========================================================================
    # 2. SEED KCET & COMEDK CUTOFFS
    # =========================================================================
    if os.path.exists(SEED_CUTOFFS):
      print(f"[*] Ingesting entrance rank cutoffs from {SEED_CUTOFFS}...")
      df_cutoffs = pd.read_csv(SEED_CUTOFFS)
      cutoffs_objs = []
      for _, row in df_cutoffs.iterrows():
        cutoffs_objs.append(
            Cutoff(
                id=str(row.get("cutoff_id", uuid.uuid4())),
                college_code=row["college_code"],
                college_name=row["college_name"],
                year=int(row["year"]),
                exam=row["exam"],
                round_name=str(row.get("round", "Round-2 (Final)")),
                branch=row["branch"],
                category=row["category"],
                cutoff_rank=int(row["cutoff_rank"]),
            )
        )
      session.bulk_save_objects(cutoffs_objs)
      session.commit()
      print(f"  [+] Ingested {len(cutoffs_objs)} Cutoff rank data points.")

    # =========================================================================
    # 3. SEED 1,050+ SYNTHETIC STUDENT PROFILES
    # =========================================================================
    if os.path.exists(SEED_STUDENTS):
      print(f"[*] Ingesting student profiles from {SEED_STUDENTS}...")
      df_students = pd.read_csv(SEED_STUDENTS)
      students_objs = []
      for _, row in df_students.iterrows():
        students_objs.append(
            Student(
                id=str(uuid.uuid4()),
                student_uid=row["student_id"],
                usn=row["usn"],
                full_name=row["full_name"],
                college_code=row["college_code"],
                college_name=row["college_name"],
                branch=row["branch"],
                grad_year=int(row.get("grad_year", 2026)),
                cgpa=float(row["cgpa"]),
                hackathons_won=int(row.get("hackathons_won", 0)),
                primary_skills=str(row.get("primary_skills", "")),
                placement_status=row["placement_status"],
                offered_ctc_lpa=float(row.get("offered_ctc_lpa", 0.0)),
                placed_company=str(row.get("placed_company", "None")),
                job_title=str(row.get("job_title", "Student")),
                linkedin_url=str(row.get("linkedin_url", "")),
                google_scholar_url=str(row.get("google_scholar_url", "")),
            )
        )
      session.bulk_save_objects(students_objs)
      session.commit()
      print(
          f"  [+] Ingested {len(students_objs)} Student verified records &"
          " skills."
      )

    # =========================================================================
    # 4. SEED OUTREACH EVENTS & PARTNER SCHOOLS
    # =========================================================================
    if os.path.exists(SEED_EVENTS):
      print(f"[*] Ingesting outreach events from {SEED_EVENTS}...")
      with open(SEED_EVENTS, "r", encoding="utf-8") as f:
        events_raw = json.load(f)

      for e in events_raw:
        event = OutreachEvent(
            event_id=e["event_id"],
            title=e["title"],
            track=e["track"],
            speaker_name=e.get("speaker_name", ""),
            speaker_designation=e.get("speaker_designation", ""),
            event_date=e.get("event_date", ""),
            event_time=e.get("event_time", ""),
            platform=e.get("platform", "Google Meet / YouTube Live"),
            registration_fee=e.get("registration_fee", "Free"),
            target_audience=e.get("target_audience", ""),
            brochure_asset=e.get("brochure_asset", ""),
            learning_outcomes=e.get("learning_outcomes", []),
        )
        session.add(event)

      # Seed Initial Outreach Partner Institutions
      partner_schools = [
          PartnerSchool(
              school_name="National Public School (Indiranagar)",
              city="Bengaluru",
              coordinator_name="Dr. Ananya Sharma",
              coordinator_email="ananya.sharma@nps.edu",
              coordinator_phone="+91 98860 11223",
              registered_batch_size=120,
              selected_program=(
                  "Free Generative AI & Prompt Engineering 2-Day Bootcamp"
              ),
              mou_signed=True,
          ),
          PartnerSchool(
              school_name="MES Pre-University College (Malleshwaram)",
              city="Bengaluru",
              coordinator_name="Prof. K. Venkatesh",
              coordinator_email="venkatesh@mes.edu",
              coordinator_phone="+91 98450 44556",
              registered_batch_size=200,
              selected_program=(
                  "Engineering Stream Selector & Career Aptitude Test"
              ),
              mou_signed=True,
          ),
          PartnerSchool(
              school_name="St. Aloysius PU College",
              city="Mangaluru",
              coordinator_name="Sr. Lancy D'Souza",
              coordinator_email="lancy@aloysius.edu",
              coordinator_phone="+91 94480 77889",
              registered_batch_size=85,
              selected_program="IoT & Robotics Discovery Lab Session",
              mou_signed=False,
          ),
          PartnerSchool(
              school_name="Base PU College",
              city="Mysuru",
              coordinator_name="Dr. H. N. Suresh",
              coordinator_email="suresh.hn@base.ac.in",
              coordinator_phone="+91 97410 33221",
              registered_batch_size=150,
              selected_program=(
                  "KCET & COMEDK Option Entry Strategy & College Rank Matcher"
              ),
              mou_signed=True,
          ),
      ]
      session.add_all(partner_schools)

      # Seed Initial High-Intent Admission Inquiries
      sample_leads = [
          AdmissionLead(
              student_name="Kavya Ramesh",
              parent_name="Ramesh Kulkarni",
              contact_email="ramesh.kulkarni@gmail.com",
              contact_phone="+91 98451 99882",
              target_college_code="E001",
              target_branch="CSE (AI & ML)",
              admission_type="Management Quota",
              entrance_rank=3200,
              exam_name="KCET",
              intent_score=5,
              query_notes=(
                  "Interested in scholarship eligibility and CoE in AI lab"
                  " facilities."
              ),
              status="New",
          ),
          AdmissionLead(
              student_name="Nikhil Deshmukh",
              parent_name="Sanjay Deshmukh",
              contact_email="sanjay.d@yahoo.com",
              contact_phone="+91 99800 44321",
              target_college_code="E002",
              target_branch="AI-DS",
              admission_type="Merit",
              entrance_rank=1420,
              exam_name="COMEDK",
              intent_score=4,
              query_notes=(
                  "Inquired regarding Round 2 cutoff projection vs hostel"
                  " booking timeline."
              ),
              status="Contacted",
          ),
      ]
      session.add_all(sample_leads)

      session.commit()
      print(
          f"  [+] Ingested {len(events_raw)} Outreach Events, Partner Schools"
          " and Initial Admission Leads."
      )

    print(
        "\n[✔] Database successfully seeded with full benchmark intelligence"
        " data!"
    )

  except Exception as e:
    session.rollback()
    print(f"[✘] Database seeding failed with error: {str(e)}")
    raise e
  finally:
    session.close()


if __name__ == "__main__":
  seed_database()
