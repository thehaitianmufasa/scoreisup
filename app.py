import streamlit as st
from db import get_user_by_email, get_connection
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Credit Tools Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Main app content
st.title("Credit Tools Portal")

# Sidebar for login/signup
with st.sidebar:
    if not st.session_state.logged_in:
        st.markdown("### Account")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            from auth import login
            login()
        with tab2:
            from auth import signup
            signup()
    else:
        st.markdown(f"### Welcome, {st.session_state.user_email}")
        if st.button("Logout"):
            from auth import logout
            logout()

# Main content area
if st.session_state.logged_in:
    st.markdown("### Your Credit Tools")
    # Add your credit tools content here
else:
    st.info("Please log in or sign up to access the credit tools.")

# Minimal CSS for a dark sidebar only
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #23272f;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
# Initialize ALL session state variables at the start
if "nav" not in st.session_state:
    st.session_state["nav"] = "Dashboard"
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "Test User"
if "user_address" not in st.session_state:
    st.session_state["user_address"] = ""
if "user_phone" not in st.session_state:
    st.session_state["user_phone"] = ""

from dashboard import show_dashboard
from dispute_letter import show_dispute_form
from settings import settings_page
from src.utils.config import APP_CONFIG

# --- AUTHENTICATION ---
if not st.session_state["logged_in"]:  # Use dictionary-style access
    auth_mode = st.radio("Select Option", ["Login", "Sign Up"])
    if auth_mode == "Login":
        login()
    else:
        signup()
else:
    with st.sidebar:
        st.title("🔧 Tools Portal")
        st.success(f"Logged in as: {st.session_state['user_name']}")
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
            st.session_state["logged_in"] = False
            st.session_state["user_name"] = ""
            st.rerun()

    if st.session_state["nav"] == "Dashboard":
        show_dashboard()
    elif st.session_state["nav"] == "Dispute Letter":
        show_dispute_form()
    elif st.session_state["nav"] == "Settings":
        settings_page()

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; margin-bottom: 10px;'>
            <a href='mailto:support@scoreisup.com' style='color: #fdbb6d; font-weight: bold; text-decoration: none; font-size: 1.1rem;'>
                📧 Contact Us
            </a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; margin: 0;'>© {APP_CONFIG['COMPANY_NAME']} 2025</p>", unsafe_allow_html=True) 
