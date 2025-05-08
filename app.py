import streamlit as st
import bcrypt
from db import insert_user, get_user_by_email

# --- Session Defaults ---
if "user" not in st.session_state:
    st.session_state["user"] = None
if "login_mode" not in st.session_state:
    st.session_state["login_mode"] = "login"

st.title("🔐 Dispute Letter Portal")

# --- Logged In View ---
if st.session_state["user"]:
    st.success(f"Welcome, {st.session_state['user']}!")
    if st.button("Logout"):
        st.session_state["user"] = None
        st.experimental_rerun()

# --- Login Flow ---
elif st.session_state["login_mode"] == "login":
    st.subheader("Log In")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    if st.button("Log In"):
        user = get_user_by_email(login_email)
        if user and bcrypt.checkpw(login_password.encode("utf-8"), user[2].encode("utf-8")):
            st.session_state["user"] = user[1]
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid email or password.")
    if st.button("Go to Sign Up"):
        st.session_state["login_mode"] = "signup"
        st.experimental_rerun()

# --- Signup Flow ---
elif st.session_state["login_mode"] == "signup":
    st.subheader("Sign Up")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Create Account"):
        if get_user_by_email(signup_email):
            st.error("Account already exists.")
        else:
            success = insert_user(signup_email, signup_password)
            if success:
                st.success("Account created! Please log in.")
                st.session_state["login_mode"] = "login"
                st.experimental_rerun()
            else:
                st.error("Error creating account.")
    if st.button("Go to Login"):
        st.session_state["login_mode"] = "login"
        st.experimental_rerun()


