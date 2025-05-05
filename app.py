import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Dispute Letter Generator", layout="centered")

st.title("📄 Dispute Letter Generator")
st.markdown("Fill in the form below to generate your PDF dispute letter automatically.")

# Input fields
client_name = st.text_input("Full Name", "Jeff Chery")
account_name = st.text_input("Account Name", "Capital One")
account_number = st.text_input("Account Number", "xxx-8592")
dispute_reason = st.text_area("Reason for Dispute", "This account was the result of identity theft and should not be on my credit file.")
address = st.text_area("Address", "3386 Mount Zion Road, Apt 713,\nStockbridge, GA 30281")
dob = st.text_input("Date of Birth", "09/22/1987")

# Generate PDF if button is clicked
if st.button("📥 Generate PDF Letter"):
    letter = f"""To Whom It May Concern,

My name is {client_name}, and I am writing to formally dispute an account on my credit report.

Account Name: {account_name}
Account Number: {account_number}

Reason for Dispute:
{dispute_reason}

Please investigate this matter and remove the account from my credit file.
I have included identification and supporting documentation.

Thank you for your time and attention to this matter.

Sincerely,
{client_name}
{address}
{dob}
"""

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in letter.strip().split("\n"):
        pdf.multi_cell(0, 10, line.strip())

    file_name = f"dispute_letter_{client_name.replace(' ', '_')}.pdf"
    pdf.output(file_name)

    with open(file_name, "rb") as f:
        st.download_button("⬇️ Download Your Letter", f, file_name=file_name, mime="application/pdf")
