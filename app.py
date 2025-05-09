import streamlit as st
from db import insert_user, get_user_by_email
import bcrypt

# Session state setup
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Login Function
def login():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("✅ Login successful. Redirecting...")
            st.session_state.force_refresh = True
        else:
            st.error("Invalid login credentials.")

# Signup Function
def signup():
    st.subheader("Create Account")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Sign Up"):
        if get_user_by_email(email):
            st.warning("Email already registered.")
        else:
            success = insert_user(email, password)
            if success:
                st.success("Account created. Please log in.")
            else:
                st.error("Sign up failed.")

# Logout Function
def logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.success("Logged out successfully.")
    st.experimental_rerun()

# Main Router Logic
st.title("📄 Credit Dispute Letter Generator")

if st.session_state.logged_in:
    st.success(f"Welcome, {st.session_state.user_email}!")
    if st.button("🔓 Logout"):
        logout()
else:
    tab = st.radio("Select Option", ["Login", "Sign Up"], key="auth_tab_radio")
    if tab == "Login":
        login()
    else:
        signup()


