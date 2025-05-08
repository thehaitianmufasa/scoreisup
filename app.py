import streamlit as st
from db import insert_user, get_user_by_email, insert_dispute_submission
import bcrypt
from fpdf import FPDF
import tempfile
import datetime

# --- Session Defaults ---
if "user" not in st.session_state:
    st.session_state["user"] = None
if "login_mode" not in st.session_state:
    st.session_state["login_mode"] = "login"

st.title("🔐 Dispute Letter Portal")

# --- Authentication Logic ---
if st.session_state["user"]:
    st.success(f"Welcome, {st.session_state['user']}!")
    if st.button("Logout"):
        st.session_state["user"] = None
        st.experimental_rerun()

elif st.session_state["login_mode"] == "login":
    st.subheader("Log In")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    if st.button("Log In"):
        user = get_user_by_email(login_email)
        if user and bcrypt.checkpw(login_password.encode('utf-8'), user[2].encode('utf-8')):
            st.session_state["user"] = user[1]
            st.experimental_rerun()
        else:
            st.error("Invalid email or password.")
    if st.button("Go to Sign Up"):
        st.session_state["login_mode"] = "signup"
        st.experimental_rerun()

elif st.session_state["login_mode"] == "signup":
    st.subheader("Sign Up")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Create Account"):
        if get_user_by_email(signup_email):
            st.error("Account already exists.")
        else:
            success = insert_user(signup_email, signup_password)
            if success:
                st.success("Account created. Please log in.")
                st.session_state["login_mode"] = "login"
                st.experimental_rerun()
            else:
                st.error("Error creating account.")
    if st.button("Go to Login"):
        st.session_state["login_mode"] = "login"
        st.experimental_rerun()

# --- Main App (Protected) ---
if st.session_state["user"]:
    st.title("📄 Credit Dispute Letter Generator")

    if "num_accounts" not in st.session_state:
        st.session_state.num_accounts = 1

    def add_account():
        if st.session_state.num_accounts < 5:
            st.session_state.num_accounts += 1

    if st.button("➕ Add Another Account") and st.session_state.num_accounts < 5:
        add_account()

    reason_texts = {
        "Account not mine (identity theft)": (
            "Re: Fraudulent Account Dispute – Identity Theft",
            "I did not open or authorize the account listed. This is a clear case of identity theft. Please remove this item under FCRA §605B and §609(a)."
        ),
        "Paid account still showing unpaid": (
            "Re: Paid Account Reporting as Unpaid",
            "This account was paid in full, but it is still showing as unpaid. Please update your records under FCRA §623(a)(2)."
        ),
        "Never late but marked late": (
            "Re: False Late Payment Reporting",
            "I have never made a late payment on this account. Please investigate and correct this mistake under FCRA §611."
        ),
        "Balance is incorrect": (
            "Re: Incorrect Balance Reporting",
            "The balance being reported is inaccurate. Please investigate and update this information under FCRA §611."
        ),
        "Account was settled but shows as charged-off": (
            "Re: Settled Account Reporting as Charged-Off",
            "This account was settled but is showing as charged-off. Please correct this to reflect accurate settlement under FCRA §623(a)."
        ),
        "Re-aged account / illegally reset": (
            "Re: Re-aged Account in Violation of FCRA",
            "The date of first delinquency appears to have been reset. This is illegal re-aging and violates FCRA §605(c)."
        ),
        "Duplicate account on report": (
            "Re: Duplicate Account Dispute",
            "This account is listed multiple times on my credit report, inflating my debt. Please remove duplicates per FCRA §611."
        ),
        "Account included in bankruptcy": (
            "Re: Bankruptcy Account Still Reporting",
            "This account was discharged in bankruptcy and should reflect a $0 balance. Please correct per FCRA §1681c."
        ),
        "Fraudulent account": (
            "Re: Fraudulent Account Dispute",
            "This account is not mine and was opened fraudulently. Please remove it under FCRA §605B and §623(a)(6)."
        ),
        "I was not an authorized user": (
            "Re: Unauthorized User Account",
            "I was never added as an authorized user. Please remove this entry under FCRA §611 and §623."
        ),
        "Incorrect payment history": (
            "Re: Inaccurate Payment History",
            "The payment history is incorrect. I request correction under FCRA §611."
        ),
        "Account already paid or settled": (
            "Re: Paid or Settled Account Still Showing Negative",
            "This account was paid or settled and should show a $0 balance. Please update it accordingly under FCRA §623(a)."
        ),
        "Wrong account status reported": (
            "Re: Incorrect Account Status",
            "The account status (e.g., charged-off, delinquent) is incorrect. Please correct under FCRA §611."
        ),
        "Outdated account info (older than 7-10 years)": (
            "Re: Removal of Outdated Account",
            "This account has exceeded the reporting limit of 7–10 years. Please remove it per FCRA §605(a)."
        ),
        "Charge-off account still updating monthly": (
            "Re: Improper Monthly Updates on Charged-Off Account",
            "This account is charged off but is still being updated monthly, which is misleading. Please cease and correct this under FCRA §623(a)(2)."
        )
    }

    with st.form("dispute_form"):
        st.subheader("🔒 Your Information")
        client_name = st.text_input("Full Name")
        address = st.text_input("Mailing Address")
        dob = st.text_input("Date of Birth (MM/DD/YYYY)")
        letter_date = st.date_input("Letter Date", value=datetime.date.today())
        email = st.text_input("Email Address")
        ssn_last4 = st.text_input("Last 4 Digits of SSN")

        st.subheader("🏢 Credit Bureau")
        bureau_options = {
            "Equifax": "Equifax\nP.O. Box 105788\nAtlanta, GA 30348",
            "Experian": "Experian\nP.O. Box 4500\nAllen, TX 75013",
            "TransUnion": "TransUnion\nP.O. Box 2000\nChester, PA 19016"
        }
        selected_bureau = st.selectbox("Select Bureau", list(bureau_options.keys()))

        st.subheader("📑 Accounts You're Disputing")
        account_fields = []
        for i in range(st.session_state.num_accounts):
            st.markdown(f"### Account #{i+1}")
            col1, col2 = st.columns(2)
            with col1:
                acct_name = st.text_input(f"Account Name {i+1}", key=f"acct_name_{i}")
            with col2:
                acct_number = st.text_input(f"Account Number {i+1}", key=f"acct_number_{i}")
            reasons = st.multiselect(f"Dispute Reasons {i+1}", list(reason_texts.keys()), key=f"reasons_{i}")
            account_fields.append((acct_name, acct_number, reasons))

        submitted = st.form_submit_button("📄 Generate Dispute Letter")

    if submitted:
        sections = [
            f"{letter_date.strftime('%B %d, %Y')}\n",
            bureau_options[selected_bureau],
            "",
            f"{client_name}\n{address}\n{email}\nDOB: {dob}\nSSN: {ssn_last4}",
            "",
            "Subject: Formal Dispute of Inaccurate Account Information",
            "",
            "Dear Sir or Madam,",
            "I am writing to dispute the following accounts. Each has been listed with errors or violations of the Fair Credit Reporting Act (FCRA). Please investigate and resolve as outlined.",
            ""
        ]

        for idx, (acct_name, acct_number, reasons) in enumerate(account_fields, 1):
            if acct_name and acct_number and reasons:
                sections += [f"---\nAccount #{idx}", f"Creditor: {acct_name}", f"Account #: {acct_number}", ""]
                for r in reasons:
                    sections.append(reason_texts[r][1])
                sections.append("")

        sections += [
            "I’ve included a copy of my ID and proof of address for verification.",
            "Please investigate and respond within 30 days, as required by law.",
            "",
            "Thank you for your prompt attention to this matter.",
            "",
            f"Sincerely,\n{client_name}"
        ]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.set_auto_page_break(auto=True, margin=15)

        for section in sections:
            for line in section.split("\n"):
                safe_line = line.encode("latin-1", "replace").decode("latin-1")
                pdf.multi_cell(0, 8, safe_line)
            pdf.ln(4)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            tmp_path = tmp.name

        insert_dispute_submission(
            client_name, email, address, dob, ssn_last4,
            selected_bureau, "Multiple reasons", letter_date
        )

        with open(tmp_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="dispute_letter.pdf")

    st.markdown("### 🧾 Get Weekly Credit Reports")
    st.link_button("Go to AnnualCreditReport.com", "https://www.annualcreditreport.com")



