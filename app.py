import streamlit as st
from datetime import datetime
import bcrypt
from db import insert_dispute_submission, insert_user, get_user_by_email

# ---------- SESSION STATE ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'auth_tab' not in st.session_state:
    st.session_state.auth_tab = "Login"

# ---------- LOGIN ----------
def login():
    st.subheader("Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            st.session_state.logged_in = True
            st.session_state.user_email = user[1]
            st.success("✅ Login successful. Redirecting...")
        else:
            st.error("Invalid email or password.")

# ---------- SIGNUP ----------
def signup():
    st.subheader("Create Account")

    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Sign Up"):
        if get_user_by_email(email):
            st.warning("Email already exists.")
        else:
            success = insert_user(email, password)
            if success:
                st.success("Account created. Please log in.")
            else:
                st.error("There was an error creating your account.")

# ---------- DISPUTE FORM ----------
def dispute_form():
    st.subheader("Generate Dispute Letter")

    name = st.text_input("Full Name")
    email = st.text_input("Email", value=st.session_state.user_email)
    address = st.text_area("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")
    ssn_last4 = st.text_input("Last 4 Digits of SSN")
    bureau = st.selectbox("Select Bureau", ["Equifax", "Experian", "TransUnion"])
    letter_date = st.date_input("Letter Date", datetime.today()).strftime("%m/%d/%Y")

    st.markdown("You can dispute up to 5 accounts below:")

    dispute_data = []
    for i in range(5):
        with st.expander(f"Account #{i+1}", expanded=(i == 0)):
            account_name = st.text_input(f"Account Name #{i+1}", key=f"acct_name_{i}")
            account_number = st.text_input(f"Account Number #{i+1}", key=f"acct_num_{i}")
            reason = st.text_area(f"Dispute Reason #{i+1}", key=f"reason_{i}")
            if account_name and account_number and reason:
                dispute_data.append((account_name, account_number, reason))

    if st.button("Generate & Submit"):
        for account in dispute_data:
            insert_dispute_submission(
                name=name,
                email=email,
                address=address,
                dob=dob,
                ssn_last4=ssn_last4,
                bureau=bureau,
                dispute_reasons=f"{account[0]} - {account[1]}: {account[2]}",
                letter_date=letter_date
            )
        st.success("Dispute letters submitted successfully!")

# ---------- MAIN ROUTER ----------
st.title("Credit Dispute Letter Generator")

# ✅ After login sets state, rerun to render the form
if st.session_state.logged_in:
    st.success(f"Welcome, {st.session_state.user_email}!")
    dispute_form()
else:
    tab = st.radio("Select Option", ["Login", "Sign Up"], key="auth_tab_radio")

    if tab == "Login":
        login()
        if st.session_state.logged_in:
            st.rerun()  # rerun after setting state to trigger redirect
    else:
        signup()
