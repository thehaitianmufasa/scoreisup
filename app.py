from fpdf import FPDF
import streamlit as st

# --- Full Dispute Mapping ---
dispute_mapping = {""" + """
""" + ',
'.join([f'"{k}": {{"subject": {repr(v["subject"])}, "body": {repr(v["body"])}}}' for k, v in {
    "Account not mine (identity theft)": {
        "subject": "Re: Urgent Request to Remove Fraudulent Account from Credit Report",
        "body": "I am writing to formally dispute an account appearing on my credit report that I did not authorize or open. After reviewing my credit file, I discovered this account, which is the result of identity theft. I did not apply for, open, or use this account in any capacity, nor have I ever had a relationship with the creditor associated with it.\n\nUnder my rights granted by the Fair Credit Reporting Act (FCRA), specifically §605B and §609(a), I request the immediate deletion of this fraudulent account from my credit profile. I have included proper identification and supporting documentation to validate my claim.\n\nPlease investigate this matter and confirm deletion in writing."
    }
}.items()]) + """
}

# Credit Bureau addresses
bureau_addresses = {
    "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
    "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
    "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
}

st.title("Credit Dispute Letter Generator")

client_name = st.text_input("Enter your full name")
account_name = st.text_input("Enter the account name")
account_number = st.text_input("Enter the account number (e.g., xxx-8592)")
address = st.text_input("Enter your mailing address")
dob = st.text_input("Enter your date of birth (MM/DD/YYYY)")
email = st.text_input("Enter your email address")
ssn_last4 = st.text_input("Enter the last 4 digits of your SSN")

bureau = st.selectbox("Select Credit Bureau", list(bureau_addresses.keys()))
reasons = st.multiselect("Select Dispute Reasons", list(dispute_mapping.keys()))

if st.button("Generate Letter"):
    subject_line = "Re: " + " & ".join([dispute_mapping[r]["subject"].replace("Re: ", "") for r in reasons])
    combined_body = "\n\n".join([dispute_mapping[r]["body"] for r in reasons])

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

    output_filename = "dispute_letter.pdf"
    pdf.output(output_filename)
    with open(output_filename, "rb") as f:
        st.download_button("Download PDF", f, file_name=output_filename)
