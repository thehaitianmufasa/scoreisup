import streamlit as st
from db import insert_dispute_submission
from fpdf import FPDF
import io
from datetime import datetime

st.title("📝 Credit Dispute Letter Generator")

with st.form("dispute_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    address = st.text_area("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")
    ssn_last4 = st.text_input("Last 4 Digits of SSN")
    bureau = st.selectbox("Choose Credit Bureau", ["Equifax", "TransUnion", "Experian"])
    dispute_reasons = st.multiselect("Choose Reason(s) for Dispute", [
        "Duplicate account still reporting",
        "Paid account still showing balance",
        "Account not mine",
        "Wrong dates reported",
        "Incorrect balance",
        "Other"
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
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"""
{letter_date.strftime('%B %d, %Y')}

To Whom It May Concern at {bureau},

I am writing to dispute the following item(s) on my credit report. Please investigate the following issue(s) as I believe there may be errors.

Name: {name}
Address: {address}
DOB: {dob}
SSN (Last 4): {ssn_last4}
Email: {email}

Reasons for dispute:
{", ".join(dispute_reasons)}

Thank you for your time and attention.

Sincerely,
{name}
""")
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        st.success("🎉 Dispute letter generated successfully!")

        st.download_button("📎 Download Dispute Letter PDF", 
                           data=pdf_output.getvalue(), 
                           file_name="dispute_letter.pdf", 
                           mime="application/pdf")
    else:
        st.error("There was an error saving your data.")

# Footer link
st.markdown("### 🔍 [Get Your Free Weekly Credit Report](https://www.annualcreditreport.com)")

