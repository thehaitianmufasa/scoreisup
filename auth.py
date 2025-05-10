import streamlit as st
import bcrypt
from db import get_user_by_email, insert_user

def login():
    st.markdown("## 🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user_by_email(email)

        # Support both password and password_hash
        stored_hash = user.get("password") or user.get("password_hash")

        if user and stored_hash and bcrypt.checkpw(password.encode(), stored_hash.encode()):
            st.session_state.logged_in = True
            st.session_state.user_email = user["email"]
            st.success(f"Welcome back, {user['email']}!")
            st.experimental_rerun()
        else:
            st.error("Invalid login credentials.")

def signup():
    st.markdown("## ✍️ Sign Up")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
            return

        user = get_user_by_email(email)
        if user:
            st.error("Email already exists!")
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        insert_user(email, hashed_pw)

        st.success("Account created successfully! You can now login.")
        st.info("Login using the same form above.")

