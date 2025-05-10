import streamlit as st
from dashboard import show_dashboard
from dispute_letter import show_dispute_form
from auth import login, signup

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Layout config
st.set_page_config(page_title="Credit Tools Portal", layout="wide", initial_sidebar_state="expanded")

# Sidebar Navigation
with st.sidebar:
    st.title("🔧 Tools Portal")
    if st.session_state.logged_in:
        st.success(f"Logged in as: {st.session_state.user_email}")
        nav = st.radio("Go to", ["Dashboard", "Dispute Letter", "Settings"])
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.experimental_rerun()
    else:
        nav = st.radio("Authenticate", ["Login", "Sign Up"])

# Main content
if st.session_state.logged_in:
    if nav == "Dashboard":
        show_dashboard()
    elif nav == "Dispute Letter":
        show_dispute_form()
    elif nav == "Settings":
        st.markdown("## ⚙️ Settings page coming soon.")
else:
    if nav == "Login":
        login()
    elif nav == "Sign Up":
        signup()
