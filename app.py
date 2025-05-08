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

# Dispute reasons and letter templates
from dispute_templates import dispute_mapping

with st.form("dispute_form"):
    client_name = st.text_input("Full Name")
    address = st.text_area("Mailing Address")
    email = st.text_input("Email Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")
    ssn_last4 = st.text_input("Last 4 Digits of SSN")
    bureau = st.selectbox("Choose Credit Bureau", list(bureau_addresses.keys()))
    dispute_reasons = st.multiselect("Choose Reason(s) for Dispute", list(dispute_mapping.keys()))
    account_name = st.text_input("Account Name")
    account_number = st.text_input("Account Number")
    letter_date = st.date_input("Select Letter Date", value=datetime.today())
    submit = st.form_submit_button("Generate Dispute Letter")

if submit:
    try:
        dob_sql = datetime.strptime(dob, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        st.error("DOB format should be MM/DD/YYYY")
        st.stop()

    success = insert_dispute_submission(
        client_name, email, address, dob_sql, ssn_last4, bureau,
        ", ".join(dispute_reasons), letter_date.strftime("%m/%d/%Y")
    )

    if success:
        subject_line = "Re: " + " & ".join([dispute_mapping[r]["subject"].replace("Re: ", "") for r in dispute_reasons])
        combined_body = ""
        for reason in dispute_reasons:
            if reason in dispute_mapping:
                combined_body += f"{dispute_mapping[reason]['body']}\n\n"

        letter_sections = [
            f"{client_name}\n{address}\n{email}\nDOB: {dob}\n",
            bureau_addresses[bureau],
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
                pdf.multi_cell(0, 8, line.strip())
            pdf.ln(4)

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
