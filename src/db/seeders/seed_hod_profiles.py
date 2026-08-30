"""
src/db/seeders/seed_hod_profiles.py

Modular Database Seeder for Department HOD Directories:
Inserts or updates Head of Department (HOD) credentials and research focus areas for core branches.
"""

from src.core.database import get_db
from src.db.models import CollegePublishedProfile


def seed_hod_profiles():
    hod_records = [
        {
            "college_code": "RVCE",
            "hod_cse": "Dr. A. Saravanan (Ph.D. IISc) — Cloud Computing & Algorithms",
            "hod_aids": "Dr. B. Sathish Babu (Ph.D. IITR) — Artificial Intelligence & Big Data",
            "hod_ece": "Dr. M. Guttedar (Ph.D. IITD) — VLSI & Embedded Systems"
        },
        {
            "college_code": "PESU",
            "hod_cse": "Dr. K. S. Shreedhara (Ph.D.) — Cyber Security & Systems",
            "hod_aids": "Dr. Sowmya Kamath (Ph.D.) — Deep Learning & NLP",
            "hod_ece": "Dr. V. Krishna Kumar (Ph.D.) — Signal Processing & Communications"
        },
        {
            "college_code": "BMSCE",
            "hod_cse": "Dr. P. Jayarekha (Ph.D.) — Distributed Databases & Security",
            "hod_aids": "Dr. D. N. Sujatha (Ph.D.) — Machine Learning & Analytics",
            "hod_ece": "Dr. Rajeshwari Hegde (Ph.D.) — Wireless Communications"
        },
        {
            "college_code": "MSRIT",
            "hod_cse": "Dr. Annamma Abraham (Ph.D.) — Artificial Intelligence & Software Engineering",
            "hod_aids": "Dr. Seema Singh (Ph.D.) — Data Science & Deep Learning",
            "hod_ece": "Dr. M. Nagabushan (Ph.D.) — Signal Processing & IoT"
        }
    ]

    try:
        with get_db() as db:
            for item in hod_records:
                profile = db.query(CollegePublishedProfile).filter_by(college_code=item["college_code"]).first()
                if profile:
                    profile.hod_cse = item["hod_cse"]
                    profile.hod_aids = item["hod_aids"]
                    profile.hod_ece = item["hod_ece"]
            db.commit()
        print("✅ Successfully seeded department HOD directories and research profiles!")
    except Exception as exc:
        print(f"Error seeding HOD profiles: {exc}")


if __name__ == "__main__":
    seed_hod_profiles()
