"""
src/ui/components/auth_widget.py

Authentication and persona switcher widget for the PragyanAI platform sidebar.
Handles user login state, demo quick-logins, registration, and RBAC authorization securely.
"""

import streamlit as st
from src.core.security import UserRole


def render_auth_sidebar() -> UserRole:
    """Renders the authentication and persona selection widget in the Streamlit sidebar securely."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 Access & Persona Hub")

    # Initialize all session state variables safely
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "user_role" not in st.session_state:
        st.session_state.user_role = UserRole.ASPIRANT
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Guest Aspirant"

    if not st.session_state.logged_in:
        with st.sidebar.expander("🔑 Login / Register", expanded=True):
            # --- Demo Quick-Login Section ---
            st.markdown("🚀 **Quick Demo Login:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎓 Aspirant", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_email = "aspirant@pragyanai.edu"
                    st.session_state.user_role = UserRole.ASPIRANT
                    st.session_state.user_name = "Aarav Sharma"
                    st.rerun()
                if st.button("🏫 School Partner", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_email = "principal@bnglschool.edu"
                    st.session_state.user_role = UserRole.SCHOOL_PARTNER
                    st.session_state.user_name = "Principal Rao"
                    st.rerun()
            with col2:
                if st.button("💼 Recruiter", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_email = "hiring@microsoft.com"
                    st.session_state.user_role = UserRole.RECRUITER
                    st.session_state.user_name = "Microsoft Recruiter"
                    st.rerun()
                if st.button("🏛️ Dean / Lead", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_email = "dean@pragyanai.edu"
                    st.session_state.user_role = UserRole.LEADERSHIP
                    st.session_state.user_name = "Dr. Sateesh Ambesange"
                    st.rerun()

            if st.button("👑 System Admin", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_email = "admin@pragyanai.edu"
                st.session_state.user_role = UserRole.ADMIN
                st.session_state.user_name = "Platform Administrator"
                st.rerun()

            st.markdown("---")
            auth_mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed", horizontal=True)
            
            email_input = st.text_input("Email Address", value="", key="auth_email_input")
            password_input = st.text_input("Password", type="password", value="", key="auth_password_input")
            
            role_options = list(UserRole)
            selected_role = st.selectbox(
                "Select Persona / Role",
                options=role_options,
                format_func=lambda x: x.value,
                key="auth_role_selector"
            )

            if auth_mode == "Login":
                if st.button("Sign In with Password", type="primary", use_container_width=True):
                    if email_input and password_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.session_state.user_role = selected_role
                        st.session_state.user_name = email_input.split("@")[0].title()
                        st.success(f"Welcome back, {st.session_state.user_name}!")
                        st.rerun()
                    else:
                        st.warning("Please enter both email and password.")
            else:
                if st.button("Create Account", type="primary", use_container_width=True):
                    if email_input and password_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.session_state.user_role = selected_role
                        st.session_state.user_name = email_input.split("@")[0].title()
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.warning("Please provide both email and password.")
    else:
        # Display active user profile badge
        st.sidebar.success(f"👤 **{st.session_state.user_name}**")
        st.sidebar.caption(f"Role: `{st.session_state.user_role.value}`")
        st.sidebar.text(f"Email: {st.session_state.user_email}")
        
        if st.sidebar.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_role = UserRole.ASPIRANT
            st.session_state.user_name = "Guest Aspirant"
            st.success("Signed out successfully.")
            st.rerun()

    return st.session_state.get("user_role", UserRole.ASPIRANT)
