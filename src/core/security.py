"""
src/core/security.py

Role-Based Access Control (RBAC), bcrypt password hashing, and user permission
authorization for PragyanAI College Intelligence Hub.
"""

import logging
from enum import Enum
from typing import Dict, List, Set, Union
import bcrypt

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """Supported user personas across the multi-role platform."""
    GUEST = "Guest / Student Aspirant"
    ASPIRANT = "Student & Parent Aspirant"
    SCHOOL_PARTNER = "School / PU Partner Desk"
    RECRUITER = "Corporate Recruiter"
    LEADERSHIP = "Dean & Institutional Leadership"
    ADMIN = "System Administrator"


# Resource permission lookup table mapping roles to authorized actions
ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
    UserRole.GUEST: {
        "view_colleges",
        "predict_cutoffs",
        "view_fee_structures",
        "chat_ai_assistant",
        "download_public_brochures",
        "view_webinars",
    },
    UserRole.ASPIRANT: {
        "view_colleges",
        "predict_cutoffs",
        "view_fee_structures",
        "chat_ai_assistant",
        "download_public_brochures",
        "view_webinars",
        "submit_admission_inquiry",
        "register_for_webinar",
        "calculate_roi",
    },
    UserRole.SCHOOL_PARTNER: {
        "view_colleges",
        "chat_ai_assistant",
        "view_webinars",
        "bulk_register_school_cohorts",
        "schedule_campus_visits",
        "access_career_aptitude_tests",
        "download_outreach_curricula",
    },
    UserRole.RECRUITER: {
        "view_colleges",
        "chat_ai_assistant",
        "search_student_talent",
        "view_student_skills_cgpa",
        "view_placement_analytics",
        "view_coe_research_grants",
        "download_recruiter_one_pagers",
    },
    UserRole.LEADERSHIP: {
        "view_colleges",
        "predict_cutoffs",
        "view_fee_structures",
        "chat_ai_assistant",
        "download_public_brochures",
        "view_webinars",
        "submit_admission_inquiry",
        "register_for_webinar",
        "calculate_roi",
        "bulk_register_school_cohorts",
        "search_student_talent",
        "view_student_skills_cgpa",
        "view_placement_analytics",
        "view_coe_research_grants",
        "download_recruiter_one_pagers",
        "view_admission_leads_crm",
        "view_naac_nba_analytics",
        "export_institutional_reports",
        "modify_college_metadata",
    },
    UserRole.ADMIN: {
        "*"  # Superuser permission wildcard
    },
}


class SecurityManager:
    """Handles password hashing, token validation, and RBAC authorization checks securely."""

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hashes a plaintext password string using bcrypt with automated salting."""
        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
            return hashed.decode("utf-8")
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Compares a plaintext password against a stored bcrypt hash safely."""
        if not plain_password or not hashed_password:
            return false
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception as e:
            logger.warning(f"Password verification error: {e}")
            return False

    @classmethod
    def has_permission(cls, role: Union[UserRole, str], permission: str) -> bool:
        """Evaluates whether a given role holds the requested permission with string normalization."""
        if isinstance(role, str):
            try:
                role = UserRole(role)
            except ValueError:
                # Try matching by enum name or value
                matched = None
                for r in UserRole:
                    if r.value.lower() == role.lower() or r.name.lower() == role.lower():
                        matched = r
                        break
                if matched:
                    role = matched
                else:
                    return False

        permissions = ROLE_PERMISSIONS.get(role, set())
        if "*" in permissions or permission in permissions:
            return True
        return False

    @classmethod
    def get_allowed_roles_for_action(cls, permission: str) -> List[UserRole]:
        """Returns the list of all roles permitted to execute an action."""
        allowed: List[UserRole] = []
        for role, perms in ROLE_PERMISSIONS.items():
            if "*" in perms or permission in perms:
                allowed.append(role)
        return allowed


# Module-level convenience functions
verify_password = SecurityManager.verify_password
get_password_hash = SecurityManager.hash_password


def require_role(current_role: Union[UserRole, str], required_permission: str) -> bool:
    """Permission guard for UI views and API endpoints with secure logging."""
    if not SecurityManager.has_permission(current_role, required_permission):
        logger.warning(f"Unauthorized access attempt: Role '{current_role}' lacked permission '{required_permission}'.")
        raise PermissionError(
            f"Access Denied: Role '{current_role}' lacks '{required_permission}' permission."
        )
    return True
