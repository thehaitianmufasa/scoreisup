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
    "Account not mine (identity theft)": ("Fraudulent Account Reporting", "This account does not belong to me and appears to be the result of identity theft. Under the Fair Credit Reporting Act (FCRA) §605B and §609(a), I am formally requesting its immediate removal. Documentation is provided to support this claim."),
    "Paid account still showing unpaid": ("Inaccurate Unpaid Status", "This account has been fully paid, yet it continues to report as unpaid. As required by FCRA §623(a)(2), please update this record to reflect the accurate status."),
    "Never late but marked late": ("False Late Payment Reporting", "This account inaccurately reflects late payments. I have never missed or submitted a late payment. Please correct this error in accordance with FCRA §611."),
    "Balance is incorrect": ("Incorrect Balance Reporting", "The balance shown for this account is not accurate. I request a prompt review and correction under FCRA §611."),
    "Account was settled but shows as charged-off": ("Improper Charge-Off Label", "This account was legally settled, yet it is still marked as charged-off. Please update the status to reflect the settlement under FCRA §623(a)."),
    "Re-aged account / illegally reset": ("Illegal Account Re-aging", "This account appears to have been re-aged illegally, in violation of FCRA §605(c). Please correct the Date of First Delinquency (DOFD) and update the reporting accordingly."),
    "Duplicate account on report": ("Duplicate Account Entry", "This account is listed more than once, which is a reporting error. Please remove the duplicate entry under FCRA §611."),
    "Account included in bankruptcy": ("Bankruptcy Discharged Account", "This account was discharged through bankruptcy and should reflect that status. Please update the record in compliance with FCRA §1681c."),
    "Fraudulent account": ("Unauthorized Account Dispute", "This is a fraudulent account that I did not authorize or open. Please remove it under FCRA §605B and §623(a)(6). Supporting documentation is attached."),
    "I was not an authorized user": ("Authorized User Error", "I was never added as an authorized user on this account. Please remove the reporting in accordance with FCRA §611 and §623."),
    "Incorrect payment history": ("Inaccurate Payment History", "The payment history for this account contains inaccuracies. Please correct the record to reflect the accurate payment history under FCRA §611."),
    "Account already paid or settled": ("Improper Status of Settled Account", "This account has been either paid or legally settled, yet it remains listed as open. Please update it to reflect a $0 balance under FCRA §623(a)."),
    "Wrong account status reported": ("Incorrect Account Status", "The account status reported is incorrect (e.g., showing as 'charged-off' or 'past due'). Please investigate and correct this under FCRA §611."),
    "Outdated account info (older than 7-10 years)": ("Outdated Reporting Violation", "This account is beyond the legally allowed reporting period and must be removed under FCRA §605(a)."),
    "Charge-off account still updating monthly": ("Illegal Re-aging of Charged-Off Account", "This charged-off account continues to report monthly activity despite no recent payment. This is considered re-aging and violates FCRA §605 and §623(a)(2). Please cease further updates.")
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
    dob = st.text_input("Date of Birth (MM/DD/YYYY)", help="Example: 05/08/1990")
    email = st.text_input("Email Address", value=st.session_state.user_email)
    ssn_last4 = st.text_input("Last 4 Digits of SSN")
    letter_date = st.date_input("Letter Date", value=date.today())

    bureau_options = {
        "Equifax": "Equifax Information Services LLC\nP.O. Box 740256\nAtlanta, GA 30374-0256",
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
    confirm_id_uploaded = st.checkbox("✅ I have included a copy of my ID (even if not uploaded here)", key="confirm_id")

    st.markdown("### 🔍 Get Your Free Weekly Credit Report")
    st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")

    if st.button("📄 Generate & Download Letter"):
        if not name or not address or not dob or not ssn_last4 or not email:
            st.warning("⚠️ Please complete all required fields before generating the letter.")
        elif not any(acct_name and acct_number and reasons for acct_name, acct_number, reasons in dispute_data):
            st.warning("⚠️ Please enter at least one valid account with dispute reasons.")
        else:
            try:
                dob_obj = datetime.strptime(dob, "%m/%d/%Y")
                dob_formatted = dob_obj.strftime("%Y-%m-%d")
            except ValueError:
                st.error("❌ Date of Birth must be in MM/DD/YYYY format.")
                return

            try:
                pdf = FPDF()
                pdf.add_page()

                # Load TTF font (must be in same directory as app.py)
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.add_font("DejaVu", "B", "DejaVuSans.ttf", uni=True)

                pdf.set_font("DejaVu", "", 12)
                pdf.multi_cell(0, 10, bureau_options[bureau])
                pdf.ln(5)
                pdf.cell(0, 10, "To Whom It May Concern:", ln=True)
                pdf.ln(5)
                pdf.multi_cell(0, 10, "I am writing to dispute inaccurate information being reported on my credit file regarding the following account(s):")
                pdf.ln(5)

                for idx, (acct_name, acct_number, reasons) in enumerate(dispute_data):
                    if acct_name and acct_number and reasons:
                        pdf.set_font("DejaVu", "B", 12)
                        pdf.cell(0, 10, f"Account {idx + 1} – Ending in {acct_number}", ln=True)
                        pdf.set_font("DejaVu", "", 12)
                        for reason in reasons:
                            header, body = reason_texts[reason]
                            pdf.multi_cell(0, 10, f"{header}: {body}")
                        pdf.ln(3)

                pdf.ln(5)
                pdf.multi_cell(0, 10, "These discrepancies are damaging to my credit profile and misrepresent my financial history. I am formally requesting the immediate deletion or full correction of the above accounts. If not corrected within 30 days as required by law, I will escalate the matter with the CFPB, FTC, and legal counsel.")
                pdf.ln(10)
                pdf.cell(0, 10, "Sincerely:", ln=True)
                pdf.ln(5)
                pdf.cell(0, 10, name, ln=True)
                pdf.cell(0, 10, address, ln=True)
                pdf.cell(0, 10, f"SSN (Last 4): {ssn_last4}", ln=True)
                pdf.cell(0, 10, f"DOB: {dob}", ln=True)
                pdf.cell(0, 10, f"Date: {letter_date.strftime('%B %d, %Y')}", ln=True)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    pdf.output(tmp.name)
                    st.success("✅ Letter generated successfully!")
                    st.download_button(
                        "📥 Download Dispute Letter",
                        data=open(tmp.name, "rb").read(),
                        file_name=f"Dispute_Letter_{name.replace(' ', '_')}_{bureau}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Failed to generate letter: {e}")

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
