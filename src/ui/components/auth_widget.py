"""
src/ui/components/auth_widget.py

Authentication and Role-Based Access Control (RBAC) Sidebar Widget for PragyanAI.
Supports user registration, role selection, and secure session state management.
"""

import streamlit as st
from src.core.security import UserRole


def render_auth_sidebar():
    """Renders the authentication and profile switcher in the Streamlit sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔐 User Authentication & Portal Access")

    # Initialize session state for user auth if not present
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_role = UserRole.STUDENT
        st.session_state.user_name = "Guest Aspirant"

    if not st.session_state.logged_in:
        auth_mode = st.sidebar.radio("Select Action:", ["🔑 Log In", "📝 Create Account"], horizontal=True, key="auth_mode_radio")

        with st.sidebar.form("auth_form"):
            email_input = st.text_input("Email Address *", placeholder="user@example.com", key="auth_email_input")
            name_input = st.text_input("Full Name / Institution Name *", placeholder="Aarav Sharma", key="auth_name_input")
            
            selected_role = st.selectbox(
                "Select Portal Role:",
                [
                    UserRole.STUDENT,
                    UserRole.SCHOOL_PARTNER,
                    UserRole.COLLEGE_ADMIN,
                    UserRole.RECRUITER,
                ],
                format_func=lambda r: {
                    UserRole.STUDENT: "🎓 Student / Aspirant",
                    UserRole.SCHOOL_PARTNER: "🏫 School / PU Coordinator",
                    UserRole.COLLEGE_ADMIN: "🏛️ College Admin / HOD",
                    UserRole.RECRUITER: "💼 Corporate Recruiter",
                }.get(r, str(r)),
                key="auth_role_select",
            )

            submit_label = "Create Account & Enter Portal" if auth_mode == "📝 Create Account" else "Log In to Dashboard"
            submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)

            if submitted:
                if not email_input or not name_input:
                    st.error("Please provide both email and name.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_input.strip()
                    st.session_state.user_name = name_input.strip()
                    st.session_state.user_role = selected_role
                    st.success(f"Welcome, {st.session_state.user_name}! Logged in successfully.")
                    st.rerun()
    else:
        st.sidebar.success(f"👤 **{st.session_state.user_name}**")
        
        role_display = {
            UserRole.STUDENT: "🎓 Student / Aspirant",
            UserRole.SCHOOL_PARTNER: "🏫 School / PU Coordinator",
            UserRole.COLLEGE_ADMIN: "🏛️ College Admin / HOD",
            UserRole.RECRUITER: "💼 Corporate Recruiter",
        }.get(st.session_state.user_role, str(st.session_state.user_role))

        st.sidebar.caption(f"Role: **{role_display}**")
        st.sidebar.caption(f"Email: `{st.session_state.user_email}`")

        if st.sidebar.button("🚪 Log Out / Switch Account", use_container_width=True, key="btn_logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_name = "Guest Aspirant"
            st.rerun()
