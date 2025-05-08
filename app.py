import streamlit as st
from db import insert_dispute_submission
from fpdf import FPDF
import io
from datetime import datetime

st.title("📄 Credit Dispute Letter Generator")

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

    letter_date = st.date_input("Select Letter Date", value=datetime.today())
    submit = st.form_submit_button("Generate Dispute Letter")

if submit:
    success = insert_dispute_submission(
        name, email, address, dob, ssn_last4, bureau,
        ", ".join(dispute_reasons), letter_date.strftime("%m/%d/%Y")
    )

    if success:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 10, f"{letter_date.strftime('%B %d, %Y')}\n")
        pdf.multi_cell(0, 10, f"{name}\n{address}\nEmail: {email}\nDOB: {dob}\nSSN (Last 4): {ssn_last4}\n")
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"To Whom It May Concern at {bureau},\n")
        pdf.multi_cell(0, 10, "I am writing to dispute the following item(s) on my credit report:\n")
        for reason in dispute_reasons:
            pdf.multi_cell(0, 10, f"• {reason}")
        pdf.ln(5)
        pdf.multi_cell(0, 10, "Please investigate and correct the inaccuracies within 30 days as required by law.\n\nSincerely,\n")
        pdf.multi_cell(0, 10, name)

        pdf_output = io.BytesIO()
        pdf_data = pdf.output(dest="S").encode("latin1")
        pdf_output.write(pdf_data)
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
