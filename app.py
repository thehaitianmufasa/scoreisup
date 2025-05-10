import streamlit as st
from streamlit_extras import stx

st.set_page_config(
    page_title="Credit Tools Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False  # Initialize logged_in as False

cookie_manager = stx.CookieManager()
cookies = cookie_manager.get_all()
if "user_email" in cookies:
    st.session_state["logged_in"] = True
    st.session_state["user_email"] = cookies["user_email"]

from dashboard import show_dashboard
from dispute_letter import show_dispute_form
from settings import settings_page
from src.utils.config import APP_CONFIG
from auth import login, signup

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
            cookie_manager.delete("user_email")
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
