import streamlit as st
import bcrypt
from db import get_user_by_email, insert_user

def login():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Invalid login credentials.")

def signup():
    st.subheader("Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    is_human = st.checkbox("✅ I am a human (required to create account)", key="signup_human")
    if st.button("Sign Up"):
        if not is_human:
            st.warning("⚠️ Please confirm you're human before signing up.")
            return
        if get_user_by_email(email):
            st.warning("Email already registered.")
        else:
            success = insert_user(email, password)
            if success:
                st.success("Account created. Please log in.")
            else:
                st.error("Sign up failed.")
