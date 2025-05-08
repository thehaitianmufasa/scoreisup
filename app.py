import streamlit as st
from datetime import datetime
from db import insert_dispute_submission, create_dispute_table
from fpdf import FPDF

# 📌 Admin-only table creation button (must be OUTSIDE the form)
if st.button("Create Table (Admin Only)"):
    create_dispute_table()

st.title("📄 Credit Dispute Letter Generator")

with st.form("dispute_form"):
    st.header("Enter Your Information")

    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    address = st.text_input("Mailing Address")
    dob_input = st.text_input("Date of Birth (MM/DD/YYYY)")
    ssn_last4 = st.text_input("Last 4 Digits of SSN")

    bureau = st.selectbox("Select Credit Bureau", ["Equifax", "Experian", "TransUnion"])

    dispute_reasons = st.multiselect("Select Reason(s) for Dispute", [
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

    letter_date_input = st.text_input("Letter Date (MM/DD/YYYY)", value=datetime.today().strftime("%m/%d/%Y"))

    submit = st.form_submit_button("Generate Dispute Letter")

    if submit:
        try:
            # Convert dates
            dob = datetime.strptime(dob_input, "%m/%d/%Y").strftime("%m/%d/%Y")
            letter_date = datetime.strptime(letter_date_input, "%m/%d/%Y").strftime("%m/%d/%Y")

            saved = insert_dispute_submission(
                name, email, address, dob, ssn_last4,
                bureau, ", ".join(dispute_reasons), letter_date
            )

            if saved:
                st.success("Submission saved to database.")

                # Generate PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=12)
                pdf.multi_cell(0, 8, f"{name}\n{address}\nEmail: {email}\nDOB: {dob}\n")
                pdf.multi_cell(0, 8, f"To: {bureau}\nDate: {letter_date}")
                pdf.ln(5)
                pdf.multi_cell(0, 8, f"Dispute Reasons:\n- " + "\n- ".join(dispute_reasons))
                pdf.ln(5)
                pdf.multi_cell(0, 8, f"SSN (Last 4): {ssn_last4}")
                pdf.ln(5)
                pdf.multi_cell(0, 8, "I have attached identification and documentation supporting my dispute. Please complete your investigation and respond within 30 days.")
                pdf.ln(10)
                pdf.multi_cell(0, 8, f"Sincerely,\n{name}")

                pdf_output = "dispute_letter.pdf"
                pdf.output(pdf_output)

                with open(pdf_output, "rb") as file:
                    st.download_button("📎 Download Dispute Letter PDF", file.read(), file_name=pdf_output)

        except ValueError:
            st.error("⚠️ Please ensure all date fields are in MM/DD/YYYY format.")

