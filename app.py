import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import bcrypt
from db import insert_dispute_submission, insert_user, get_user_by_email

st.set_page_config(page_title="📄 Credit Dispute Letter Generator", layout="centered")

# --- Session Setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "num_accounts" not in st.session_state:
    st.session_state.num_accounts = 1

def add_account():
    if st.session_state.num_accounts < 5:
        st.session_state.num_accounts += 1

def logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.num_accounts = 1
    st.success("Logged out successfully.")
    st.experimental_rerun()

def login():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("✅ Login successful. Redirecting...")
            st.session_state.force_refresh = True
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
    st.markdown("## 🔒 Your Information")
    client_name = st.text_input("Full Name")
    address = st.text_input("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")
    letter_date = st.date_input("Select Letter Date", value=datetime.date.today())
    email = st.text_input("Email Address", value=st.session_state.user_email)
    ssn_last4 = st.text_input("Last 4 Digits of SSN")

    st.markdown("## 🏢 Choose Credit Bureau")
    bureau_options = {
        "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
        "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
        "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
    }
    selected_bureau = st.selectbox("Credit Bureau", list(bureau_options.keys()))

    st.markdown("## 🧾 Account(s) You're Disputing")
    if st.button("➕ Add Another Account"):
        add_account()

    account_fields = []
    for i in range(st.session_state.num_accounts):
        st.markdown(f"### 📄 Account #{i+1}")
        cols = st.columns([1, 1])
        with cols[0]:
            acct_name = st.text_input(f"Account Name {i+1}", key=f"acct_name_{i}")
        with cols[1]:
            acct_number = st.text_input(f"Account Number {i+1}", key=f"acct_number_{i}")
        selected_reasons = st.multiselect(f"Select Reason(s) for Account #{i+1}", list(reason_texts.keys()), key=f"reasons_{i}")
        account_fields.append((acct_name, acct_number, selected_reasons))

    st.markdown("## 📥 Upload Supporting Documents")
    id_upload = st.file_uploader("Upload a Photo ID (Driver's License, Passport)", type=["jpg", "jpeg", "png", "pdf"])
    proof_upload = st.file_uploader("Upload Proof of Address (Utility Bill, Lease, etc.)", type=["jpg", "jpeg", "png", "pdf"])

    submitted = st.button("📄 Generate Dispute Letter")

    if submitted:
        sections = [
            f"{letter_date.strftime('%B %d, %Y')}\n",
            bureau_options[selected_bureau],
            "",
            f"{client_name}\n{address}\n{email}\nDOB: {dob}\nSSN (Last 4): {ssn_last4}",
            "",
            "Subject: Dispute of Multiple Inaccurate Accounts – Request for Immediate Correction",
            "",
            "Dear Sir/Madam,",
            "",
            "I am writing to formally dispute the following accounts appearing on my credit report. Each contains inaccurate, outdated, or legally improper information. I have detailed each account below along with my dispute reason and request for correction in accordance with the Fair Credit Reporting Act (FCRA).",
            ""
        ]

        for idx, (acct_name, acct_number, reasons) in enumerate(account_fields, 1):
            if acct_name and acct_number and reasons:
                sections += [
                    "---",
                    f"Account #{idx}",
                    f"Creditor: {acct_name}",
                    f"Account Number: {acct_number}",
                    ""
                ]
                for r in reasons:
                    sections.append(reason_texts[r][1])
                    sections.append("")

        sections += [
            "I have attached a copy of my government-issued ID and proof of address to validate this dispute.",
            "Please complete your investigation and respond in writing within the 30-day window as required by federal law.",
            "",
            "Thank you for your time and attention to this matter.",
            "",
            f"Sincerely,\n{client_name}"
        ]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=12)

        for section in sections:
            for line in section.strip().split("\n"):
                safe_line = line.encode("latin-1", "replace").decode("latin-1")
                pdf.multi_cell(0, 8, safe_line)
            pdf.ln(4)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            tmp_path = tmp.name

        insert_dispute_submission(
            client_name, email, address, dob, ssn_last4,
            selected_bureau,
            "Multiple reasons per account",
            letter_date
        )

        with open(tmp_path, "rb") as f:
            st.download_button("📥 Download Your Dispute Letter", f, file_name="dispute_letter.pdf")

        st.markdown("### 🔍 Get Your Free Weekly Credit Report")
        st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")

# --- UI ROUTER ---
st.title("📄 Credit Dispute Letter Generator")

if st.session_state.logged_in:
    st.success(f"Welcome, {st.session_state.user_email}!")
    if st.button("🔓 Logout"):
        logout()
    dispute_form()
else:
    tab = st.radio("Select Option", ["Login", "Sign Up"], key="auth_tab_radio")
    if tab == "Login":
        login()
        if st.session_state.get("force_refresh"):
            del st.session_state["force_refresh"]
            st.experimental_rerun()
    else:
        signup()

# --- Footer ---
st.markdown("### 🔍 Get Your Free Weekly Credit Report")
st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")

