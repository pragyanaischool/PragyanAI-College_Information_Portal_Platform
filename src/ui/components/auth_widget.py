"""
src/ui/components/auth_widget.py

Authentication and persona switcher widget for the PragyanAI platform sidebar.
Handles user login state, registration, role selection, and RBAC authorization.
"""

import streamlit as st
from src.core.security import UserRole


def render_auth_sidebar() -> UserRole:
    """Renders the authentication and persona selection widget in the Streamlit sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 Access & Persona Hub")

    # Initialize session state variables safely using valid UserRole enums
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_role = UserRole.ASPIRANT  # Fixed: UserRole.STUDENT -> UserRole.ASPIRANT
        st.session_state.user_name = "Guest Aspirant"

    if not st.session_state.logged_in:
        with st.sidebar.expander("🔑 Login / Register", expanded=True):
            auth_mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed")
            
            email_input = st.text_input("Email Address", key="auth_email_input")
            password_input = st.text_input("Password", type="password", key="auth_password_input")
            
            # Role selection for demo/testing or registration
            role_options = list(UserRole)
            selected_role = st.selectbox(
                "Select Persona / Role",
                options=role_options,
                format_func=lambda x: x.value,
                key="auth_role_selector"
            )

            if auth_mode == "Login":
                if st.button("Sign In", type="primary", use_container_width=True):
                    if email_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.session_state.user_role = selected_role
                        st.session_state.user_name = email_input.split("@")[0].title()
                        st.success(f"Welcome back, {st.session_state.user_name}!")
                        st.rerun()
                    else:
                        st.error("Please enter a valid email address.")
            else:
                if st.button("Create Account", type="primary", use_container_width=True):
                    if email_input and password_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.session_state.user_role = selected_role
                        st.session_state.user_name = email_input.split("@")[0].title()
                        st.success("Account created and signed in successfully!")
                        st.rerun()
                    else:
                        st.error("Please provide both email and password.")
    else:
        # Display active user profile badge
        st.sidebar.success(f"👤 **{st.session_state.user_name}**")
        st.sidebar.caption(f"Role: `{st.session_state.user_role.value}`")
        
        if st.sidebar.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_role = UserRole.ASPIRANT
            st.session_state.user_name = "Guest Aspirant"
            st.success("Signed out successfully.")
            st.rerun()

    return st.session_state.user_role
