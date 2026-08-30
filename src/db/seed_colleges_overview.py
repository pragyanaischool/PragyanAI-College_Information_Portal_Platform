"""
src/db/seeders/seed_colleges_overview.py

Modular Database Seeder for Institutional Overviews & Quick Facts:
Inserts or updates essential institution telemetry, NAAC grades, NIRF ranks, 
and placement CTC packages into the central PragyanAI database.
"""

from src.core.database import get_db
from src.db.models import CollegePublishedProfile


def seed_colleges_overview():
    """Seeds or updates core institution overview records."""
    overview_data = [
        {
            "college_code": "RVCE",
            "college_name": "RV College of Engineering",
            "city": "Bengaluru Urban, Karnataka",
            "naac_grade": "A++ (CGPA 3.64)",
            "nirf_rank": 38,
            "median_ctc": 16.86,
            "highest_ctc": 67.0,
            "placement_rate": 96.5
        },
        {
            "college_code": "PESU",
            "college_name": "PES University (Ring Road Campus)",
            "city": "Bengaluru Urban, Karnataka",
            "naac_grade": "A++ (CGPA 3.71)",
            "nirf_rank": 45,
            "median_ctc": 14.83,
            "highest_ctc": 65.0,
            "placement_rate": 97.2
        },
        {
            "college_code": "BMSCE",
            "college_name": "BMS College of Engineering",
            "city": "Bengaluru Urban, Karnataka",
            "naac_grade": "A++ (CGPA 3.83)",
            "nirf_rank": 72,
            "median_ctc": 11.4,
            "highest_ctc": 51.5,
            "placement_rate": 94.0
        },
        {
            "college_code": "MSRIT",
            "college_name": "MS Ramaiah Institute of Technology",
            "city": "Bengaluru North, Karnataka",
            "naac_grade": "A+ (CGPA 3.48)",
            "nirf_rank": 65,
            "median_ctc": 12.0,
            "highest_ctc": 50.0,
            "placement_rate": 95.2
        },
        {
            "college_code": "DSCE",
            "college_name": "Dayananda Sagar College of Engineering",
            "city": "Bengaluru Urban, Karnataka",
            "naac_grade": "A+ (CGPA 3.56)",
            "nirf_rank": 82,
            "median_ctc": 9.5,
            "highest_ctc": 56.0,
            "placement_rate": 93.5
        },
        {
            "college_code": "SJCE",
            "college_name": "Sri Jayachamarajendra College of Engineering (JSS STU)",
            "city": "Mysuru, Karnataka",
            "naac_grade": "A+ (CGPA 3.52)",
            "nirf_rank": 85,
            "median_ctc": 9.8,
            "highest_ctc": 44.0,
            "placement_rate": 92.0
        },
        {
            "college_code": "NIE",
            "college_name": "National Institute of Engineering (NIE)",
            "city": "Mysuru, Karnataka",
            "naac_grade": "A+ (CGPA 3.45)",
            "nirf_rank": 94,
            "median_ctc": 9.2,
            "highest_ctc": 40.0,
            "placement_rate": 91.5
        }
    ]

    try:
        with get_db() as db:
            for item in overview_data:
                profile = db.query(CollegePublishedProfile).filter_by(college_code=item["college_code"]).first()
                if profile:
                    for key, val in item.items():
                        setattr(profile, key, val)
                else:
                    profile = CollegePublishedProfile(**item)
                    db.add(profile)
            db.commit()
        print(f"✅ Successfully seeded overview telemetry for {len(overview_data)} institutions!")
    except Exception as exc:
        print(f"Error seeding college overview data: {exc}")


if __name__ == "__main__":
    seed_colleges_overview()
