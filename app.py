import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
from db import insert_dispute_submission

st.title("📄 Credit Dispute Letter Generator")

# --- Session State for Multi-Account Support ---
if "num_accounts" not in st.session_state:
    st.session_state.num_accounts = 1

def add_account():
    if st.session_state.num_accounts < 5:
        st.session_state.num_accounts += 1

# --- Outside Form: Add Another Account Button ---
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
    ),
    "Re-aged account / illegally reset": (
        "Re: Dispute of Re-Aged Account in Violation of FCRA",
        "The date of first delinquency on this account has been reset, which is illegal re-aging. This violates FCRA §605(c). Please correct or remove the account immediately."
    ),
    "Duplicate account on report": (
        "Re: Duplicate Account Reporting Dispute",
        "This account appears multiple times on my credit report with the same details. It’s artificially inflating my debt. Please remove the duplicate per FCRA §611."
    ),
    "Account included in bankruptcy": (
        "Re: Account Included in Bankruptcy Still Reporting",
        "This account was discharged in bankruptcy and should reflect that status. As required under FCRA §1681c, update this account to show ‘included in bankruptcy’ with a $0 balance."
    ),
    "Fraudulent account": (
        "Re: Immediate Removal of Fraudulent Account",
        "I am disputing this account as fraudulent. I did not authorize or open it, and it does not belong to me. Under FCRA §605B and §623(a)(6), this tradeline must be removed."
    ),
    "I was not an authorized user": (
        "Re: Unauthorized User Account Dispute",
        "I was never added to this account as an authorized user. I had no permission, access, or benefit from it. Please remove this listing under FCRA §611 and §623."
    ),
    "Incorrect payment history": (
        "Re: Dispute of Inaccurate Payment History",
        "The payment history on this account is incorrect and misrepresents my financial behavior. I request a full investigation and correction in accordance with FCRA §611."
    ),
    "Account already paid or settled": (
        "Re: Paid/Settled Account Still Reporting Open",
        "This account was either fully paid or settled — yet it's still showing as unpaid or delinquent. This must be updated to show $0 balance under FCRA §623(a)."
    ),
    "Wrong account status reported": (
        "Re: Incorrect Account Status Needs Correction",
        "The current status (e.g., 'charged-off', 'late') is incorrect. Please investigate and correct this reporting under FCRA §611."
    ),
    "Outdated account info (older than 7-10 years)": (
        "Re: Removal Request for Outdated Negative Account",
        "This account has surpassed the legal reporting limits — 7 years for most accounts, 10 years for bankruptcy. Please remove it as required by FCRA §605(a)."
    ),
    "Charge-off account still updating monthly": (
        "Re: Improper Updating of Charged-Off Account",
        "This account was charged off but is still being updated monthly, which is misleading and may violate re-aging restrictions. Please stop further updates and correct the status under FCRA §605 and §623(a)(2)."
    )
}


# --- FORM ---
with st.form("dispute_form"):
    st.markdown("## 🔒 Your Information")
    client_name = st.text_input("Full Name")
    address = st.text_input("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)", help="Used to match your identity during bureau review.")
    letter_date = st.date_input("Select Letter Date", value=datetime.date.today())
    email = st.text_input("Email Address")
    ssn_last4 = st.text_input("Last 4 Digits of SSN", help="Only used for ID verification in your dispute letter.")

    st.markdown("## 🏢 Choose Credit Bureau")
    bureau_options = {
        "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
        "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
        "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
    }
    selected_bureau = st.selectbox("Credit Bureau", list(bureau_options.keys()))

    st.markdown("## 🧾 Account(s) You're Disputing")
    account_fields = []
    for i in range(st.session_state.num_accounts):
        st.markdown(f"### 📄 Account #{i+1}")
        cols = st.columns([1, 1])
        with cols[0]:
            acct_name = st.text_input(f"Account Name {i+1}", key=f"acct_name_{i}")
        with cols[1]:
            acct_number = st.text_input(f"Account Number {i+1}", key=f"acct_number_{i}")
        account_fields.append((acct_name, acct_number))

    st.markdown("## ⚖️ Reason(s) for Dispute")
    selected_reasons = st.multiselect("Select Reason(s)", list(reason_texts.keys()))

    st.markdown("## 📥 Upload Supporting Documents")
    id_upload = st.file_uploader("Upload a Photo ID (Driver's License, Passport)", type=["jpg", "jpeg", "png", "pdf"])
    proof_upload = st.file_uploader("Upload Proof of Address (Utility Bill, Lease, etc.)", type=["jpg", "jpeg", "png", "pdf"])
    confirmation = st.checkbox("✅ I’ve included a copy of my ID and proof of address")

    submitted = st.form_submit_button("📄 Generate Dispute Letter")

# --- PDF GENERATION ---
if submitted and selected_reasons and confirmation:
    subject_line = "Re: " + " & ".join([reason_texts[r][0] for r in selected_reasons])
    combined_body = "\n\n".join([reason_texts[r][1] for r in selected_reasons])

    account_section = "\n".join([
        f"Account Name: {name}\nAccount Number: {number}\n"
        for name, number in account_fields if name and number
    ])

    sections = [
        f"{client_name}\n{address}\n{email}\nDOB: {dob}\n",
        bureau_options[selected_bureau],
        f"\n{subject_line}\n",
        "Dear Sir/Madam,\n",
        combined_body.strip(),
        account_section,
        "I have attached a copy of my government-issued ID and proof of address to validate this dispute. "
        "Please complete your investigation and provide a response in writing within the 30-day window as required under federal law.",
        "Thank you for your time and attention to this matter.",
        f"Sincerely,\n{client_name}\nSSN (Last 4 Digits): {ssn_last4}\nDOB: {dob}\nDate: {letter_date.strftime('%B %d, %Y')}"
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
        ", ".join(selected_reasons),
        letter_date
    )

    with open(tmp_path, "rb") as f:
        st.download_button("📥 Download Your Dispute Letter", f, file_name="dispute_letter.pdf")

# --- Footer ---
st.markdown("### 🔍 Get Your Free Weekly Credit Report")
st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")


