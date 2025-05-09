import streamlit as st
from datetime import datetime, date
import bcrypt
import tempfile
from fpdf import FPDF
from db import insert_dispute_submission, insert_user, get_user_by_email

st.set_page_config(page_title="Credit Dispute Letter Generator", layout="centered")

# ---------- SESSION STATE ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if "num_accounts" not in st.session_state:
    st.session_state.num_accounts = 1

# ---------- REASON LIBRARY ----------
reason_texts = {
    "Account not mine (identity theft)": ("Urgent Request to Remove Fraudulent Account from Credit Report", "This account is the result of identity theft. Under FCRA §605B and §609(a), I request the immediate deletion. Proper ID and documentation are included."),
    "Paid account still showing unpaid": ("Dispute Regarding Paid Account Still Reporting as Unpaid", "I am writing to dispute the inaccurate reporting of an account that I have fully paid. Under FCRA §623(a)(2), furnishers must correct inaccurate information. Documentation enclosed."),
    "Never late but marked late": ("Request to Correct False Late Payment Reporting", "I have never submitted a late payment on this account. The record is inaccurate and violates FCRA §611. Please review and correct the false entry."),
    "Balance is incorrect": ("Incorrect Balance Dispute on Reported Account", "The balance reported is incorrect and must be updated under FCRA §611."),
    "Account was settled but shows as charged-off": ("Dispute Regarding Settled Account Incorrectly Marked as Charged-Off", "This account was legally settled but shows as charged-off. Please update it under FCRA §623(a)."),
    "Re-aged account / illegally reset": ("Dispute of Re-aged Account in Violation of Federal Law", "The date of first delinquency has been illegally reset. Under FCRA §605(c), correct or remove this account."),
    "Duplicate account on report": ("Dispute of Duplicate Account Entry on Credit Report", "This account appears more than once. Please remove the duplicate per FCRA §611."),
    "Account included in bankruptcy": ("Dispute of Bankruptcy-Related Account Reporting", "This account was discharged in bankruptcy and must reflect that status under FCRA §1681c."),
    "Fraudulent account": ("Urgent Dispute - Fraudulent Account Reporting", "I am disputing a fraudulent account I did not authorize. Please remove under FCRA §605B and §623(a)(6)."),
    "I was not an authorized user": ("Dispute – Inaccurate Authorized User Status", "I was not added as an authorized user. Please remove under FCRA §611 and §623."),
    "Incorrect payment history": ("Request for Correction of Inaccurate Payment History", "The payment history is incorrect. Please correct under FCRA §611."),
    "Account already paid or settled": ("Dispute of Account Reported as Unpaid Despite Settlement", "This account was paid/settled but still shows open. Please update to $0 balance under FCRA §623(a)."),
    "Wrong account status reported": ("Correction Request for Wrong Account Status", "The account status is wrong (e.g. 'charged-off'). Please investigate under FCRA §611."),
    "Outdated account info (older than 7-10 years)": ("Request for Removal of Outdated Account Information", "This account is past legal reporting limits. Please remove it under FCRA §605(a)."),
    "Charge-off account still updating monthly": ("Illegal Re-aging of Charged-Off Account", "This charged-off account continues updating monthly without payment. Please stop updates under FCRA §605 and §623(a)(2).")
}

# ---------- HELPERS ----------
def add_account():
    if st.session_state.num_accounts < 5:
        st.session_state.num_accounts += 1

def logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.num_accounts = 1
    st.success("Logged out successfully.")

def login():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Invalid login credentials.")

def signup():
    st.subheader("Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        if get_user_by_email(email):
            st.warning("Email already registered.")
        else:
            success = insert_user(email, password)
            if success:
                st.success("Account created. Please log in.")
            else:
                st.error("Sign up failed.")

def dispute_form():
    st.subheader("📄 Generate Dispute Letter")

    name = st.text_input("Full Name")
    address = st.text_input("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")
    email = st.text_input("Email Address", value=st.session_state.user_email)
    ssn_last4 = st.text_input("Last 4 Digits of SSN")
    letter_date = st.date_input("Letter Date", value=date.today())

    bureau_options = {
        "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
        "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
        "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
    }
    bureau = st.selectbox("Select Credit Bureau", list(bureau_options.keys()))

    if st.button("➕ Add Another Account"):
        add_account()

    dispute_data = []
    for i in range(st.session_state.num_accounts):
        with st.expander(f"Account #{i+1}", expanded=(i == 0)):
            account_name = st.text_input(f"Account Name {i+1}", key=f"acct_name_{i}")
            account_number = st.text_input(f"Account Number {i+1}", key=f"acct_number_{i}")
            reasons = st.multiselect(f"Dispute Reason(s) for Account {i+1}", list(reason_texts.keys()), key=f"reasons_{i}")
            dispute_data.append((account_name, account_number, reasons))

    id_upload = st.file_uploader("Upload a Photo ID", type=["jpg", "jpeg", "png", "pdf"])
    proof_upload = st.file_uploader("Upload Proof of Address", type=["jpg", "jpeg", "png", "pdf"])

    if st.button("📄 Generate & Download Letter"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=12)

        sections = [
            f"{letter_date.strftime('%B %d, %Y')}",
            bureau_options[bureau],
            f"{name}\n{address}\n{email}\nDOB: {dob}\nSSN: {ssn_last4}",
            "",
            "Subject: Dispute of Multiple Inaccurate Accounts – Request for Immediate Correction",
            "",
            "Dear Sir/Madam,",
            "",
            "I am writing to formally dispute the following accounts appearing on my credit report. Each contains inaccurate, outdated, or legally improper information."
        ]

        for idx, (acct_name, acct_number, reasons) in enumerate(dispute_data, 1):
            if acct_name and acct_number and reasons:
                sections.append(f"\n---\nAccount #{idx}: {acct_name}\nAccount Number: {acct_number}\n")
                for reason in reasons:
                    sections.append(reason_texts[reason][1])

        sections += [
            "\nI have attached a copy of my government-issued ID and proof of address.",
            "Please complete your investigation and respond in writing within the 30-day window required by federal law.",
            f"\nThank you for your time and attention.\n\nSincerely,\n{name}"
        ]

        for section in sections:
            for line in section.strip().split("\n"):
                safe_line = line.encode("latin-1", "replace").decode("latin-1")
                pdf.multi_cell(0, 8, safe_line)
            pdf.ln(2)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            tmp_path = tmp.name

        insert_dispute_submission(
            name, email, address, dob, ssn_last4,
            bureau,
            "Multiple reasons per account",
            letter_date
        )

        with open(tmp_path, "rb") as f:
            st.download_button("📥 Download Dispute Letter", f, file_name="dispute_letter.pdf")

        st.markdown("### 🔍 Get Your Free Weekly Credit Report")
        st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")

# ---------- MAIN ROUTER ----------
st.title("Credit Dispute Letter Generator")

if st.session_state.logged_in:
    st.success(f"Welcome, {st.session_state.user_email}!")
    if st.button("🔓 Logout"):
        logout()
        st.rerun()
    dispute_form()
else:
    tab = st.radio("Select Option", ["Login", "Sign Up"], key="auth_tab_radio")
    if tab == "Login":
        login()
    else:
        signup()


