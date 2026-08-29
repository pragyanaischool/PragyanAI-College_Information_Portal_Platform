"""
src/ui/app.py

Main application entrance and RBAC page router for PragyanAI College Intelligence Hub.
"""
import sys
from pathlib import Path

# Resolve repository root (3 levels up from src/ui/app.py)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
  sys.path.insert(0, str(ROOT_DIR))
    
import importlib
import streamlit as st
from src.core.config import settings
from src.core.security import UserRole
from src.ui.components.auth_widget import render_auth_sidebar
from src.ui.styles import inject_custom_css

# Page Configuration
st.set_page_config(
    page_title="PragyanAI College Intelligence Hub",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global styling
inject_custom_css()

# Render Auth & Persona Switcher
active_role = render_auth_sidebar()

# Route dynamic view based on active persona
if active_role in [UserRole.GUEST.value, UserRole.ASPIRANT.value]:
    view_module = importlib.import_module("src.ui.views.1_🎓_Aspirant_Desk")
    view_module.render_aspirant_view()

elif active_role == UserRole.SCHOOL_PARTNER.value:
    view_module = importlib.import_module("src.ui.views.2_🏫_School_Partner")
    view_module.render_school_partner_view()

elif active_role == UserRole.RECRUITER.value:
    view_module = importlib.import_module("src.ui.views.3_💼_Recruiter_Desk")
    view_module.render_recruiter_view()

elif active_role == UserRole.LEADERSHIP.value:
    view_module = importlib.import_module("src.ui.views.4_🏛️_Leadership_View")
    view_module.render_leadership_view()
