"""
src/db/seeders/seed_governance.py

Modular Database Seeder for Executive Governance & Leadership Statements:
Inserts or updates Principal names, leadership messages, and institutional strategic visions.
"""

from src.core.database import get_db
from src.db.models import CollegePublishedProfile


def seed_governance_data():
    governance_records = [
        {
            "college_code": "RVCE",
            "principal_name": "Dr. K. N. Subramanya",
            "principal_statement": "RVCE is committed to excellence in technical education, research, and entrepreneurial incubation, fostering leaders who solve complex global engineering challenges.",
            "institutional_vision": "Leadership in Quality Technical Education, Interdisciplinary Research & Innovation."
        },
        {
            "college_code": "PESU",
            "principal_name": "Dr. J. Suryaprasad",
            "principal_statement": "Providing students with rigorous domain expertise, continuous hackathon culture, and direct exposure to top global product engineering environments.",
            "institutional_vision": "Creating professionally superior and ethically strong manpower through advanced technology education."
        },
        {
            "college_code": "BMSCE",
            "principal_name": "Dr. S. Muralidhara",
            "principal_statement": "We empower students through experiential learning, industry immersion, ethical values, and inclusive high-tech engineering education.",
            "institutional_vision": "Promoting Prosperity through Technology by imparting quality technical education."
        },
        {
            "college_code": "MSRIT",
            "principal_name": "Dr. N. V. R. Naidu",
            "principal_statement": "Our focus lies in bridging academic theory with industrial execution, ensuring our graduates lead innovation across core and computing domains.",
            "institutional_vision": "To evolve into an institution of international repute in technical education and research."
        }
    ]

    try:
        with get_db() as db:
            for item in governance_records:
                profile = db.query(CollegePublishedProfile).filter_by(college_code=item["college_code"]).first()
                if profile:
                    profile.principal_name = item["principal_name"]
                    profile.principal_statement = item["principal_statement"]
                    profile.institutional_vision = item["institutional_vision"]
            db.commit()
        print("✅ Successfully seeded executive governance & leadership statements!")
    except Exception as exc:
        print(f"Error seeding governance data: {exc}")


if __name__ == "__main__":
    seed_governance_data()
