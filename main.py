import streamlit as st
from dashboard import show_dashboard
from dispute_letter import show_dispute_form
from auth import login, signup
from src.utils.config import APP_CONFIG

# Set page config first
st.set_page_config(
    page_title="Credit Tools Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if "nav" not in st.session_state:
    st.session_state["nav"] = "Dashboard"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Test User"

# Force login for all users (bypass authentication for testing)
st.session_state.logged_in = True

# Sidebar Navigation
with st.sidebar:
    st.title("🔧 Tools Portal")
    st.success(f"Logged in as: {st.session_state.user_name}")
    nav = st.radio(
        "Go to",
        ["Dashboard", "Dispute Letter", "Settings"],
        index=["Dashboard", "Dispute Letter", "Settings"].index(st.session_state["nav"]),
        key="nav_radio"
    )
    if nav != st.session_state["nav"]:
        st.session_state["nav"] = nav
        st.rerun()
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.rerun()

# Main content
if st.session_state["nav"] == "Dashboard":
    show_dashboard()
elif st.session_state["nav"] == "Dispute Letter":
    show_dispute_form()
elif st.session_state["nav"] == "Settings":
    st.markdown("## ⚙️ Settings")
    st.markdown("### User Profile")
    with st.form("profile_form"):
        name = st.text_input("Name", value=st.session_state.user_name)
        submitted = st.form_submit_button("Update Profile")
        if submitted:
            st.session_state.user_name = name
            st.success("Profile updated!")

# Footer (no logo, no image)
st.markdown("---")
st.markdown(f"<p style='text-align: center; margin: 0;'>© {APP_CONFIG['COMPANY_NAME']} 2025</p>", unsafe_allow_html=True)

