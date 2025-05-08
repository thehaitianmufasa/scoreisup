import streamlit as st
from db import insert_dispute_submission
from fpdf import FPDF
import io
from datetime import datetime

st.title("📄 Credit Dispute Letter Generator")

bureau_addresses = {
    "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
    "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
    "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
}

with st.form("dispute_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    address = st.text_input("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")
    ssn_last4 = st.text_input("Last 4 Digits of SSN")
    bureau = st.selectbox("Choose Credit Bureau", ["Equifax", "TransUnion", "Experian"])

    dispute_reasons = st.multiselect("Choose Reason(s) for Dispute", [
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
    ])

    account_name = st.text_input("Account Name")
    account_number = st.text_input("Account Number")
    letter_date = st.date_input("Select Letter Date", value=datetime.today())
    submit = st.form_submit_button("Generate Dispute Letter")

if submit:
    success = insert_dispute_submission(
        name, email, address, dob, ssn_last4, bureau,
        ", ".join(dispute_reasons), letter_date.strftime("%m/%d/%Y")
    )

    if success:
        subject_line = "Re: " + " & ".join(dispute_reasons[:2]) + " Reporting" if len(dispute_reasons) else "Re: Credit Report Dispute"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 10, f"{name}\n{address}\n\n{email}\nDOB: {dob}\n")
        pdf.ln(2)
        pdf.multi_cell(0, 10, bureau_addresses[bureau])
        pdf.ln(2)
        pdf.multi_cell(0, 10, subject_line)
        pdf.ln(2)
        pdf.multi_cell(0, 10, "Dear Sir/Madam,")
        pdf.ln(4)

        for reason in dispute_reasons:
            pdf.multi_cell(0, 10, f"- {reason}")
            pdf.ln(1)

        pdf.ln(3)
        pdf.multi_cell(0, 10, f"Account Name: {account_name}\nAccount Number: {account_number}\n")
        pdf.ln(2)
        pdf.multi_cell(0, 10, "I have attached identification and supporting documentation to validate this dispute. Please complete your investigation and provide a response in writing within the 30-day window as required under federal law.")
        pdf.ln(3)
        pdf.multi_cell(0, 10, "Thank you for your time and attention to this matter.")
        pdf.ln(4)
        pdf.multi_cell(0, 10, f"Sincerely,\n{name}\nSSN (Last 4 Digits): {ssn_last4}\nDOB: {dob}")

        pdf_output = io.BytesIO()
        pdf_output.write(pdf.output(dest="S").encode("latin-1"))
        pdf_output.seek(0)

        st.success("🎉 Dispute letter generated successfully!")
        st.download_button("📎 Download Dispute Letter PDF",
                           data=pdf_output,
                           file_name="dispute_letter.pdf",
                           mime="application/pdf")
    else:
        st.error("❌ There was an error saving your submission. Please try again.")

st.markdown("""
---
### 🔍 Get Your Free Weekly Credit Report  
[Visit AnnualCreditReport.com](https://www.annualcreditreport.com)
""")


