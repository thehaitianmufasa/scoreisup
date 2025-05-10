import streamlit as st
from src.utils.config import APP_CONFIG

def settings_page():
    st.markdown("## ⚙️ Settings")
    st.markdown("### User Profile")
    with st.form("profile_form"):
        name = st.text_input("Name", value=st.session_state.user_name)
        address = st.text_input("Address", value=st.session_state.user_address)
        phone = st.text_input("Phone Number", value=st.session_state.user_phone)
        submitted = st.form_submit_button("Update Profile")
        if submitted:
            st.session_state.user_name = name
            st.session_state.user_address = address
            st.session_state.user_phone = phone
            st.success("Profile updated!")

    st.subheader("Change Password")

    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("Update Password"):
        # This section is removed as per the new version of the file
        pass

