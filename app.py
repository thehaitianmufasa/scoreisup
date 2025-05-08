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

# --- Authentication ---
if st.session_state["user"]:
    st.caption(f"Logged in as: {st.session_state['user']}")
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
            st.success("Login successful!")
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
            "I did not open or authorize the account listed. This is a clear case of identity theft. I have never had any dealings with this creditor and demand this be removed under FCRA §605B and §609(a)."
        ),
        "Paid account still showing unpaid": (
            "Re: Dispute of Paid Account Still Reporting as Unpaid",
            "This account was paid in full, yet it continues to report as unpaid. Please update your records accordingly under FCRA §623(a)(2)."
        ),
        "Never late but marked late": (
            "Re: False Late Payment Reporting Dispute",
            "This account is showing a late payment I never made. I request immediate correction under FCRA §611."
        ),
        # Add others as needed...
    }

    with st.form("dispute_form"):
        st.subheader("🔒 Your Information")
        client_name = st.text_input("Full Name")
        address = st.text_input("Mailing Address")
        dob = st.text_input("Date of Birth (MM/DD/YYYY)")
        letter_date = st.date_input("Letter Date", value=datetime.date.today())
        email = st.text_input("Email Address")
        ssn_last4 = st.text_input("Last 4 Digits of SSN")

        st.subheader("🏢 Choose Credit Bureau")
        bureau_options = {
            "Equifax": "Equifax\nP.O. Box 105788\nAtlanta, GA 30348",
            "Experian": "Experian\nP.O. Box 4500\nAllen, TX 75013",
            "TransUnion": "TransUnion\nP.O. Box 2000\nChester, PA 19016"
        }
        selected_bureau = st.selectbox("Credit Bureau", list(bureau_options.keys()))

        st.subheader("📄 Accounts You're Disputing")
        account_fields = []
        for i in range(st.session_state.num_accounts):
            st.markdown(f"### Account #{i+1}")
            cols = st.columns(2)
            with cols[0]:
                acct_name = st.text_input(f"Account Name {i+1}", key=f"acct_name_{i}")
            with cols[1]:
                acct_number = st.text_input(f"Account Number {i+1}", key=f"acct_number_{i}")
            selected_reasons = st.multiselect(f"Dispute Reason(s) for Account {i+1}", list(reason_texts.keys()), key=f"reasons_{i}")
            account_fields.append((acct_name, acct_number, selected_reasons))

        st.subheader("📎 Upload Supporting Docs")
        st.file_uploader("Photo ID", type=["jpg", "jpeg", "png", "pdf"])
        st.file_uploader("Proof of Address", type=["jpg", "jpeg", "png", "pdf"])

        submitted = st.form_submit_button("📄 Generate Dispute Letter")

    if submitted:
        sections = [
            f"{letter_date.strftime('%B %d, %Y')}\n",
            bureau_options[selected_bureau],
            "",
            f"{client_name}\n{address}\n{email}\nDOB: {dob}\nSSN: {ssn_last4}",
            "",
            "Subject: Dispute of Multiple Inaccurate Accounts",
            "",
            "Dear Sir or Madam,",
            "I am writing to formally dispute the following accounts. Please review each account below for inaccuracies as outlined.",
            ""
        ]

        for idx, (acct_name, acct_number, reasons) in enumerate(account_fields, 1):
            if acct_name and acct_number and reasons:
                sections += [f"---\nAccount #{idx}", f"Creditor: {acct_name}", f"Account #: {acct_number}", ""]
                for reason in reasons:
                    sections.append(reason_texts[reason][1])
                    sections.append("")

        sections += [
            "I have enclosed identification and proof of address.",
            "Please investigate and respond in writing within 30 days.",
            "",
            f"Thank you,\n{client_name}"
        ]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.set_auto_page_break(auto=True, margin=15)
        for section in sections:
            for line in section.split("\n"):
                pdf.multi_cell(0, 8, line.encode("latin-1", "replace").decode("latin-1"))
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

    st.markdown("### 🔎 Get Weekly Credit Report")
    st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com")


