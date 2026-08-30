"""
src/db/run_all_seeders.py

Master Execution Runner:
Executes all modular database seeders in proper sequence to fully populate 
the PragyanAI College Intelligence database.
"""

from src.db.seeders.seed_colleges_overview import seed_colleges_overview
from src.db.seeders.seed_governance import seed_governance_data
from src.db.seeders.seed_hod_profiles import seed_hod_profiles
from src.db.seeders.seed_recruiter_partners import seed_recruiter_partners


def run_all_seeders():
    print("🚀 Starting Modular Database Seeding Sequence...")
    
    print("\n[1/4] Seeding College Overviews & Telemetry...")
    seed_colleges_overview()
    
    print("\n[2/4] Seeding Executive Governance & Principal Statements...")
    seed_governance_data()
    
    print("\n[3/4] Seeding Department HOD Profiles & Research Focus...")
    seed_hod_profiles()
    
    print("\n[4/4] Seeding Recruiter Job Postings & Partnership Logs...")
    seed_recruiter_partners()
    
    print("\n🎉 All modular database seeders executed successfully!")


if __name__ == "__main__":
    run_all_seeders()
