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

# --- Logged In ---
if st.session_state["user"]:
    st.caption(f"Logged in as: {st.session_state['user']}")
    if st.button("Logout"):
        st.session_state["user"] = None
        st.session_state["_rerun_trigger"] = True
        st.stop()

# --- Not Logged In ---
elif st.session_state["login_mode"] == "login":
    st.subheader("Log In")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    if st.button("Log In"):
        user = get_user_by_email(login_email)
        if user and bcrypt.checkpw(login_password.encode('utf-8'), user[2].encode('utf-8')):
            st.session_state["user"] = user[1]
            st.success("Login successful!")
            st.session_state["_rerun_trigger"] = True
            st.stop()
        else:
            st.error("Invalid email or password.")
    if st.button("Go to Sign Up"):
        st.session_state["login_mode"] = "signup"
        st.session_state["_rerun_trigger"] = True
        st.stop()

# --- Sign Up Flow ---
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
                st.success("Account created! Please log in.")
                st.session_state["login_mode"] = "login"
                st.experimental_rerun()
            else:
                st.error("Error creating account.")
    if st.button("Go to Login"):
        st.session_state["login_mode"] = "login"
        st.experimental_rerun()

# --- Protected Area ---
if st.session_state["user"]:
    st.title("📄 Credit Dispute Letter Generator")

    if "num_accounts" not in st.session_state:
        st.session_state.num_accounts = 1

    def add_account():
        if st.session_state.num_accounts < 5:
            st.session_state.num_accounts += 1

    if st.session_state.num_accounts < 5:
        if st.button("➕ Add Another Account"):
            add_account()

    reason_texts = {
        "Account not mine (identity theft)": (
            "Re: Fraudulent Account Dispute – Identity Theft",
            "I did not open or authorize the account listed. This is a clear case of identity theft. I have never had any dealings with this creditor and demand this be removed under FCRA §605B and §609(a). Supporting documentation and ID are provided."
        ),
        "Paid account still showing unpaid": (
            "Re: Dispute of Paid Account Still Reporting as Unpaid",
            "This account was paid in full, yet it continues to report as unpaid. This is inaccurate reporting and a violation of FCRA §623(a)(2). I’ve included payment proof — please update your records accordingly."
        ),
        "Never late but marked late": (
            "Re: False Late Payment Reporting Dispute",
            "This account is showing a late payment I never made. I have always paid on time. I request immediate correction under FCRA §611 to reflect the true payment history."
        ),
        "Balance is incorrect": (
            "Re: Incorrect Balance Being Reported",
            "The balance listed for this account is wrong. It does not reflect my actual payment or current status. Please investigate and correct this per FCRA §611."
        ),
        "Account was settled but shows as charged-off": (
            "Re: Settled Account Reported as Charged-Off",
            "This account was legally settled, yet it’s being reported as charged-off. This is misleading and inaccurate. Update the status to reflect 'settled' under FCRA §623(a)."
        )
        # Add more as needed
    }

    with st.form("dispute_form"):
        st.markdown("## 🔒 Your Information")
        client_name = st.text_input("Full Name")
        address = st.text_input("Mailing Address")
        dob = st.text_input("Date of Birth (MM/DD/YYYY)")
        letter_date = st.date_input("Select Letter Date", value=datetime.date.today())
        email = st.text_input("Email Address")
        ssn_last4 = st.text_input("Last 4 Digits of SSN")

        st.markdown("## 🏢 Choose Credit Bureau")
        bureau_options = {
            "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
            "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
            "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
        }
        selected_bureau = st.selectbox("Credit Bureau", list(bureau_options.keys()))

        st.markdown("## 📜 Account(s) You're Disputing")
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

        st.markdown("## 📅 Upload Supporting Documents")
        id_upload = st.file_uploader("Upload a Photo ID", type=["jpg", "jpeg", "png", "pdf"])
        proof_upload = st.file_uploader("Upload Proof of Address", type=["jpg", "jpeg", "png", "pdf"])

        submitted = st.form_submit_button("📄 Generate Dispute Letter")

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
