"""
src/ui/components/auth_widget.py

Persona and Role Selection widget managing active Streamlit session states.
"""

import streamlit as st
from src.core.security import UserRole


def render_auth_sidebar() -> str:
    """Renders the role-based navigation controller on the sidebar."""
    if "user_role" not in st.session_state:
        st.session_state.user_role = UserRole.ASPIRANT.value

    st.sidebar.markdown(
        """
        <div style="text-align: center; padding-bottom: 1rem;">
            <h2 style="margin: 0; color: #1e3a8a; font-weight: 800; font-size: 1.4rem;">🏛️ PragyanAI Hub</h2>
            <p style="margin: 0; color: #64748b; font-size: 0.8rem; font-weight: 500;">College Intelligence & Decision Portal</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### 👤 Select Access Persona")
    selected_role = st.sidebar.selectbox(
        "Current Active Role:",
        [
            UserRole.ASPIRANT.value,
            UserRole.SCHOOL_PARTNER.value,
            UserRole.RECRUITER.value,
            UserRole.LEADERSHIP.value,
        ],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state.user_role = selected_role

    st.sidebar.divider()
    st.sidebar.markdown("### 🌐 Regional Language")
    lang = st.sidebar.selectbox(
        "Language:",
        ["English", "ಕನ್ನಡ (Kannada)", "हिंदी (Hindi)", "தமிழ் (Tamil)", "తెలుగు (Telugu)"],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state.selected_language = lang

    st.sidebar.divider()
    st.sidebar.markdown(
        """
        <div style="font-size: 0.75rem; color: #94a3b8; line-height: 1.4;">
            <b>System Version:</b> 1.0.0-PROD<br>
            <b>Engine:</b> LangGraph + Groq Llama 3.3 70B<br>
            <b>Vector Store:</b> ChromaDB (MiniLM-L6-v2)
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selected_role
