import streamlit as st
from db import get_user_by_email, get_connection
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- EMAIL VERIFICATION LOGIC ---
params = st.query_params
email = params.get("email", [None])[0]
token = params.get("token", [None])[0]

logger.info(f"Verification attempt - Email: {email}, Token: {token}")

if email and token:
    user = get_user_by_email(email)
    if not user:
        logger.error(f"User not found: {email}")
        st.error("User not found.")
    elif user.get("verified"):
        logger.info(f"User already verified: {email}")
        st.info("Your email is already verified.")
    elif user.get("verification_token") != token:
        logger.error(f"Invalid token for user {email}. Expected: {user.get('verification_token')}, Got: {token}")
        st.error("Invalid or expired verification link.")
    else:
        try:
            conn = get_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET verified = %s, verification_token = NULL WHERE email = %s",
                    (True, email)
                )
                conn.commit()
                cursor.close()
                conn.close()
                logger.info(f"Successfully verified user: {email}")
                st.success("Your email has been verified! You can now log in.")
            else:
                logger.error("Database connection failed")
                st.error("Verification failed: Database connection error")
        except Exception as e:
            logger.error(f"Verification failed for {email}: {str(e)}")
            st.error(f"Verification failed: {str(e)}")
    st.stop()

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
