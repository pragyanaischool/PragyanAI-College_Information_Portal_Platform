"""
src/db/__init__.py

Database package initialization for PragyanAI College Intelligence Hub.
Exposes core ORM models and repository interfaces.
"""

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
from src.db.repository import CollegeRepository

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
    "CollegeRepository",
]
