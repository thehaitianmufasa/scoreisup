
import streamlit as st
from fpdf import FPDF
import tempfile
import datetime

st.title("📄 Credit Dispute Letter Generator")

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

    dispute_options = [
        "Account not mine (identity theft)",
        "Paid account still showing unpaid",
        "Never late but marked late",
        "Balance is incorrect",
        "Account was settled but shows as charged-off",
        "Re-aged account / illegally reset",
        "Duplicate account on report",
        "Account included in bankruptcy",
        "Fraudulent account",
        "I was not an authorized user",
        "Incorrect payment history",
        "Account already paid or settled",
        "Wrong account status reported",
        "Outdated account info (older than 7-10 years)",
        "Charge-off account still updating monthly"
    ]

    selected_reasons = st.multiselect("Choose Reason(s) for Dispute", dispute_options, key="dispute_reasons")

    submitted = st.form_submit_button("Generate Dispute Letter")

reason_texts = {
    "Account not mine (identity theft)": (
        "Urgent Request to Remove Fraudulent Account from Credit Report",
        "I am writing to formally dispute an account appearing on my credit report that I did not authorize or open. After reviewing my credit file, I discovered this account, which is the result of identity theft. I did not apply for, open, or use this account in any capacity, nor have I ever had a relationship with the creditor associated with it.\n\nUnder my rights granted by the Fair Credit Reporting Act (FCRA), specifically §605B and §609(a), I request the immediate deletion of this fraudulent acco...
    ),
    "Paid account still showing unpaid": (
        "Dispute Regarding Paid Account Still Reporting as Unpaid",
        "I am writing to dispute the inaccurate reporting of an account that has been fully paid yet continues to appear as unpaid on my credit report. I have satisfied the balance in full, and this continued misreporting is damaging and misleading.\n\nUnder the Fair Credit Reporting Act (FCRA) §623(a)(2), furnishers are required to update and correct any inaccurate or incomplete information they provide. I respectfully request immediate correction of this account status to reflect its paid nature.\n\n...
    ),
    "Fraudulent account": (
        "Urgent Dispute - Fraudulent Account Reporting",
        "I am disputing an account listed on my credit file that is the result of fraudulent activity. I did not open, authorize, or have any knowledge of this account until reviewing my credit report.\n\nAs provided under FCRA §605B and §623(a)(6), I am exercising my right to request removal of this unauthorized tradeline due to fraud. I have attached a copy of my identity verification and supporting materials to validate this claim.\n\nPlease delete this account and confirm the action in writing."
    )
}

if submitted:
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
        "I have attached identification and supporting documentation to validate this dispute. Please complete your investigation and provide a response in writing within the 30-day window as required under federal law.",
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

    with open(tmp_path, "rb") as f:
        st.download_button("📥 Download Your Dispute Letter", f, file_name="dispute_letter.pdf")

st.markdown("### 🔍 Get Your Free Weekly Credit Report")
st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")
