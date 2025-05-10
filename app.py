import streamlit as st

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
if "nav" not in st.session_state:
    st.session_state["nav"] = "Dashboard"
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "Test User"
if "user_address" not in st.session_state:
    st.session_state["user_address"] = ""
if "user_phone" not in st.session_state:
    st.session_state["user_phone"] = ""

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

# Main content area
if st.session_state.logged_in:
    from dashboard import show_dashboard
    from dispute_letter import show_dispute_form
    from settings import settings_page
    from src.utils.config import APP_CONFIG
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
