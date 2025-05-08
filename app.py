import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
from db import insert_dispute_submission

st.title("📄 Credit Dispute Letter Generator")

# --- Form ---
with st.form("dispute_form"):
    client_name = st.text_input("Full Name")
    account_name = st.text_input("Account Name")
    account_number = st.text_input("Account Number (e.g., xxx-8592)")
    address = st.text_input("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")
    letter_date = st.date_input("Select Letter Date", value=datetime.date.today())
    email = st.text_input("Email Address")
    ssn_last4 = st.text_input("Last 4 Digits of SSN")

    bureau_options = {
        "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
        "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
        "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
    }
    selected_bureau = st.selectbox("Choose Credit Bureau", list(bureau_options.keys()))

    dispute_options = ['Account not mine (identity theft)', 'Paid account still showing unpaid', 'Never late but marked late', 'Balance is incorrect', 'Account was settled but shows as charged-off', 'Re-aged account / illegally reset', 'Duplicate account on report', 'Account included in bankruptcy', 'Fraudulent account', 'I was not an authorized user', 'Incorrect payment history', 'Account already paid or settled', 'Wrong account status reported', 'Outdated account info (older than 7-10 years)', 'Charge-off account still updating monthly']

    reason_texts = {
        "Account not mine (identity theft)": (
            "Urgent Request to Remove Fraudulent Account from Credit Report",
            """I am writing to formally dispute an account appearing on my credit report that I did not authorize or open.
This account is the result of identity theft. Under FCRA §605B and §609(a), I request the immediate deletion.
Proper ID and documentation are included."""
        ),
        "Paid account still showing unpaid": (
            "Dispute Regarding Paid Account Still Reporting as Unpaid",
            """I am writing to dispute the inaccurate reporting of an account that I have fully paid.
Under FCRA §623(a)(2), furnishers must correct inaccurate information. Documentation enclosed."""
        ),
        "Never late but marked late": (
            "Request to Correct False Late Payment Reporting",
            """I have never submitted a late payment on this account. The record is inaccurate and violates FCRA §611.
Please review the payment history and correct or remove the false entry."""
        ),
        "Balance is incorrect": (
            "Incorrect Balance Dispute on Reported Account",
            """The balance reported on this account is incorrect. It does not reflect the correct amount owed, paid, or settled.
Please investigate and update it under FCRA §611."""
        ),
        "Account was settled but shows as charged-off": (
            "Dispute Regarding Settled Account Incorrectly Marked as Charged-Off",
            """This account was legally settled, but it's reported as charged-off.
Under FCRA §623(a), this is incorrect reporting. Please correct it to 'settled'."""
        ),
        "Re-aged account / illegally reset": (
            "Dispute of Re-aged Account in Violation of Federal Law",
            """This account appears to have been re-aged. The date of first delinquency should remain fixed.
Under FCRA §605(c), please correct the reporting date or remove the account."""
        ),
        "Duplicate account on report": (
            "Dispute of Duplicate Account Entry on Credit Report",
            """This account appears more than once with nearly identical details, inflating my debt unfairly.
Under FCRA §611, I request removal of the duplicate entry."""
        ),
        "Account included in bankruptcy": (
            "Dispute of Bankruptcy-Related Account Reporting",
            """This account was discharged in bankruptcy and must be reported as such.
Per FCRA §1681c, please update the status to 'included in bankruptcy' with a $0 balance."""
        ),
        "Fraudulent account": (
            "Urgent Dispute - Fraudulent Account Reporting",
            """I am disputing a fraudulent account on my credit report. I did not open or authorize this tradeline.
Under FCRA §605B and §623(a)(6), I request its removal. Supporting documents attached."""
        ),
        "I was not an authorized user": (
            "Dispute – Inaccurate Authorized User Status",
            """I was never added to this account by the primary user and should not be listed.
Under FCRA §611 and §623, please remove this tradeline immediately."""
        ),
        "Incorrect payment history": (
            "Request for Correction of Inaccurate Payment History",
            """The payment history reported for this account contains errors.
Please investigate and correct any inaccuracies under FCRA §611."""
        ),
        "Account already paid or settled": (
            "Dispute of Account Reported as Unpaid Despite Settlement",
            """This account has been paid or legally settled, yet is still reported as open or delinquent.
Please update to reflect a $0 balance and correct status under FCRA §623(a)."""
        ),
        "Wrong account status reported": (
            "Correction Request for Wrong Account Status",
            """The current status reflects 'charged-off' or '120 days late' which is incorrect.
Please verify and correct this under FCRA §611."""
        ),
        "Outdated account info (older than 7-10 years)": (
            "Request for Removal of Outdated Account Information",
            """This negative account has exceeded the legal reporting limit of 7 years (or 10 for bankruptcy).
Please remove it under FCRA §605(a)."""
        ),
        "Charge-off account still updating monthly": (
            "Illegal Re-aging of Charged-Off Account",
            """A charged-off account should not continue updating monthly unless active payments are being made.
Please investigate for re-aging violations under FCRA §605 and §623(a)(2)."""
        )
    }

    selected_reasons = st.multiselect("Choose Reason(s) for Dispute", dispute_options)
    submitted = st.form_submit_button("Generate Dispute Letter")

if submitted and selected_reasons:
    subject_line = "Re: " + " & ".join([reason_texts[r][0] for r in selected_reasons])
    combined_body = ""
    for reason in selected_reasons:
        combined_body += reason_texts[reason][1] + "\n\n"

    sections = [
        f"{client_name}\n{address}\n{email}\nDOB: {dob}\n",
        bureau_options[selected_bureau],
        f"\n{subject_line}\n",
        "Dear Sir/Madam,\n",
        combined_body.strip(),
        f"Account Name: {account_name}\nAccount Number: {account_number}\n",
        "I have attached identification and supporting documentation to validate this dispute. "
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

    # Save to MySQL
    insert_dispute_submission(
        client_name, email, address, dob, ssn_last4,
        selected_bureau,
        ", ".join(selected_reasons),
        letter_date
    )

    with open(tmp_path, "rb") as f:
        st.download_button("📥 Download Your Dispute Letter", f, file_name="dispute_letter.pdf")

st.markdown("### 🔍 Get Your Free Weekly Credit Report")
st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")

