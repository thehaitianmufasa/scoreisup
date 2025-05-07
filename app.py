
import streamlit as st
from fpdf import FPDF
import tempfile

# --- Full Dispute Mapping ---
dispute_mapping = {
    "Account not mine (identity theft)": {
        "subject": "Re: Urgent Request to Remove Fraudulent Account from Credit Report",
        "body": "I am writing to formally dispute an account appearing on my credit report that I did not authorize or open. After reviewing my credit file, I discovered this account, which is the result of identity theft. I did not apply for, open, or use this account in any capacity, nor have I ever had a relationship with the creditor associated with it.\n\nUnder my rights granted by the Fair Credit Reporting Act (FCRA), specifically §605B and §609(a), I request the immediate deletion of this fraudulent account from my credit profile. I have included proper identification and supporting documentation to validate my claim.\n\nPlease investigate this matter and confirm deletion in writing."
    },
    "Fraudulent account": {
        "subject": "Re: Urgent Dispute - Fraudulent Account Reporting",
        "body": "I am disputing an account listed on my credit file that is the result of fraudulent activity. I did not open, authorize, or have any knowledge of this account until reviewing my credit report.\n\nAs provided under FCRA §605B and §623(a)(6), I am exercising my right to request removal of this unauthorized tradeline due to fraud. I have attached a copy of my identity verification and supporting materials to validate this claim.\n\nPlease delete this account and confirm the action in writing."
    }
}

bureau_addresses = {
    "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
    "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
    "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
}

st.title("📄 Credit Dispute Letter Generator")

with st.form("dispute_form"):
    client_name = st.text_input("Full Name")
    account_name = st.text_input("Account Name")
    account_number = st.text_input("Account Number (e.g., xxx-8592)")
    address = st.text_input("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")
    email = st.text_input("Email Address")
    ssn_last4 = st.text_input("Last 4 Digits of SSN")

    selected_bureau = st.selectbox("Choose Credit Bureau", list(bureau_addresses.keys()))
    selected_reasons = st.multiselect("Select Dispute Reason(s)", list(dispute_mapping.keys()), default=["Account not mine (identity theft)"])

    submitted = st.form_submit_button("Generate Dispute Letter")

if submitted:
    subject_line = "Re: " + " & ".join([dispute_mapping[r]["subject"].replace("Re: ", "") for r in selected_reasons])
    combined_body = ""
    for reason in selected_reasons:
        entry = dispute_mapping[reason]
        combined_body += f"{entry['body']}\n\n"

    letter_sections = [
        f"{client_name}\n{address}\n{email}\nDOB: {dob}\n",
        bureau_addresses[selected_bureau],
        f"\n{subject_line}\n",
        "Dear Sir/Madam,\n",
        combined_body.strip(),
        f"Account Name: {account_name}\nAccount Number: {account_number}\n",
        "I have attached identification and supporting documentation to validate this dispute. Please complete your investigation and provide a response in writing within the 30-day window as required under federal law.",
        "Thank you for your time and attention to this matter.",
        f"Sincerely,\n{client_name}\nSSN (Last 4 Digits): {ssn_last4}\nDOB: {dob}"
    ]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=12)

    for section in letter_sections:
        for line in section.strip().split("\n"):
            safe_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 8, safe_line)
        pdf.ln(4)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        st.download_button("📥 Download Your Dispute Letter", f, file_name="dispute_letter.pdf")

# 🔗 Extra Resource
st.markdown("### 🔍 Get Your Free Weekly Credit Report")
st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")
