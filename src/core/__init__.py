"""
src/core/__init__.py

Core package initialization for PragyanAI College Intelligence Hub.
Exports centralized settings, database connection sessions, schema initializers,
and role-based security handlers.
"""

from src.core.config import Settings, settings
from src.core.database import (
    Base,
    SessionLocal,
    check_db_health,
    engine,
    get_db,
    get_db_session,
    init_db,
)
from src.core.security import (
    ROLE_PERMISSIONS,
    SecurityManager,
    UserRole,
    get_password_hash,
    require_role,
    verify_password,
)

__all__ = [
    "settings",
    "Settings",
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "get_db_session",
    "init_db",
    "check_db_health",
    "UserRole",
    "SecurityManager",
    "ROLE_PERMISSIONS",
    "verify_password",
    "get_password_hash",
    "require_role",
]
