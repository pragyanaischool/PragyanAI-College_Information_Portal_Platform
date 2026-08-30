"""
src/db/seeders/seed_recruiter_partners.py

Modular Database Seeder for Recruiter Job Postings & Partnerships:
Inserts or updates corporate recruiter job descriptions, CTC ranges, and TPO communications.
"""

from src.core.database import get_db
from src.db.models import RecruiterJobPosting


def seed_recruiter_partners():
    job_postings = [
        {
            "college_code": "RVCE",
            "company_name": "Google",
            "recruiter_name": "Sarah Jenkins",
            "recruiter_email": "sjenkins@google.com",
            "target_role": "Software Engineer (New Grad)",
            "ctc_range": "₹ 28 - 45 LPA",
            "drive_date": "2026-09-15",
            "message_to_tpo": "Looking forward to our annual on-campus technical coding evaluation and hackathon finals."
        },
        {
            "college_code": "PESU",
            "company_name": "Microsoft",
            "recruiter_name": "David Miller",
            "recruiter_email": "dmiller@microsoft.com",
            "target_role": "Cloud Infrastructure Engineer",
            "ctc_range": "₹ 24 - 38 LPA",
            "drive_date": "2026-09-22",
            "message_to_tpo": "Excited to partner for AI & Cloud computing senior capstone showcases."
        },
        {
            "college_code": "BMSCE",
            "company_name": "Amazon",
            "recruiter_name": "Priya Sharma",
            "recruiter_email": "priya.sharma@amazon.com",
            "target_role": "SDE-1 (AWS Core)",
            "ctc_range": "₹ 22 - 35 LPA",
            "drive_date": "2026-10-05",
            "message_to_tpo": "Please share shortlisted student candidate resumes meeting the 8.0+ CGPA benchmark."
        }
    ]

    try:
        with get_db() as db:
            for item in job_postings:
                existing = db.query(RecruiterJobPosting).filter_by(
                    college_code=item["college_code"], 
                    company_name=item["company_name"]
                ).first()
                if not existing:
                    db.add(RecruiterJobPosting(**item))
            db.commit()
        print("✅ Successfully seeded benchmark recruiter job postings and partnership logs!")
    except Exception as exc:
        print(f"Error seeding recruiter partner data: {exc}")


if __name__ == "__main__":
    seed_recruiter_partners()
