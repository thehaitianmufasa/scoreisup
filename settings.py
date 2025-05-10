import streamlit as st
import bcrypt
from db import get_user_by_email, update_user_password

def settings_page():
    st.subheader("🔐 Change Password")

    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("Update Password"):
        user = get_user_by_email(st.session_state.user_email)

        if not user:
            st.error("User not found.")
            return

        if not bcrypt.checkpw(current_password.encode(), user[2].encode()):
            st.error("❌ Current password is incorrect.")
            return

        if new_password != confirm_password:
            st.warning("⚠️ New passwords do not match.")
            return

        if update_user_password(user[1], new_password):
            st.success("✅ Password updated successfully.")
        else:
            st.error("❌ Failed to update password.")
