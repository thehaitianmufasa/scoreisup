import streamlit as st
import bcrypt
from db import get_user_by_email, insert_user

def login():
    st.markdown("## 🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        user = get_user_by_email(email)
        
        if not user:
            st.error("Invalid email or password.")
            return

        stored_hash = user.get("password")
        if not stored_hash:
            st.error("Account error: No password hash found. Please contact support.")
            return

        try:
            # Ensure both the stored hash and input password are properly encoded
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                st.session_state.logged_in = True
                st.session_state.user_email = user["email"]
                st.success(f"Welcome back, {user['email']}!")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password.")
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")

def signup():
    st.markdown("## ✍️ Sign Up")

    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

    if st.button("Sign Up"):
        if not email or not password or not confirm_password:
            st.error("Please fill in all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match!")
            return

        if len(password) < 8:
            st.error("Password must be at least 8 characters long.")
            return

        user = get_user_by_email(email)
        if user:
            st.error("Email already exists!")
            return

        try:
            # Pass the raw password to insert_user (hashing is done in db.py)
            if insert_user(email, password):
                st.success("Account created successfully! You can now login.")
                st.info("Login using the same form above.")
            else:
                st.error("Failed to create account. Please try again.")
        except Exception as e:
            st.error(f"Error creating account: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")

