import streamlit as st
import bcrypt
from db import get_user_by_email, insert_user

def login():
    st.markdown("## 🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user_by_email(email)

        if user and "password" in user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            # Set session state
            st.session_state.logged_in = True
            st.session_state.user_email = user["email"]
            st.session_state.user_name = user.get("name", user["email"])  # fallback to email if no name column
            st.success(f"Welcome back, {st.session_state.user_name}!")
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
