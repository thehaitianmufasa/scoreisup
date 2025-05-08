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
    address = st.text_area("Mailing Address")
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

# Letter templates from original logic (expanded)
letter_templates = {
    "Account not mine (identity theft)": "I am writing to formally dispute an account appearing on my credit report that I did not authorize or open. After reviewing my credit file, I discovered this account, which is the result of identity theft. I did not apply for, open, or use this account in any capacity, nor have I ever had a relationship with the creditor associated with it.\n\nUnder my rights granted by the Fair Credit Reporting Act (FCRA), specifically §605B and §609(a), I request the immediate deletion of this fraudulent account from my credit profile. I have included proper identification and supporting documentation to validate my claim.\n\nPlease investigate this matter and confirm deletion in writing.",
    "Paid account still showing unpaid": "I am writing to dispute the inaccurate reporting of an account that has been fully paid yet continues to appear as unpaid on my credit report. I have satisfied the balance in full, and this continued misreporting is damaging and misleading.\n\nUnder the Fair Credit Reporting Act (FCRA) §623(a)(2), furnishers are required to update and correct any inaccurate or incomplete information they provide. I respectfully request immediate correction of this account status to reflect its paid nature.\n\nSupporting documentation is enclosed. Please investigate and confirm the update in writing.",
    "Never late but marked late": "I am disputing the accuracy of reported late payments associated with this account. I have never missed or submitted a late payment, and my records reflect consistent, on-time activity throughout the life of this account.\n\nReporting false delinquencies constitutes a violation under FCRA §611 and causes undue harm to my credit profile. I request that you investigate this entry, verify the payment history, and remove any inaccurate notations from my report.\n\nI have included evidence and supporting records for your review.",
    "Balance is incorrect": "I am formally disputing the balance currently reported for the account listed above. The figure does not accurately reflect the amount owed, paid, or settled. This discrepancy may be due to reporting delays or data entry errors, but it must be corrected.\n\nPursuant to FCRA §611, I request that the reporting furnisher verify the correct balance and promptly update the credit file to reflect the accurate amount.\n\nPlease find supporting documentation attached. I appreciate your cooperation in resolving this matter.",
    "Account was settled but shows as charged-off": "I am disputing the current status of this account, which inaccurately reports as charged-off despite being settled. I negotiated and completed a settlement agreement with the creditor, and as such, the status should reflect 'settled' rather than 'charged-off.'\n\nUnder FCRA §623(a), creditors are legally obligated to report information accurately and fairly. I respectfully request that the tradeline be corrected to show the true status.\n\nAttached are relevant documents supporting the settlement. Please investigate and amend accordingly.",
    "Re-aged account / illegally reset": "I am disputing the reporting of an account that appears to have been re-aged in violation of federal credit reporting laws. The date of first delinquency (DOFD) should remain fixed, yet this account continues to reflect an updated or extended timeline that inaccurately prolongs its presence on my report.\n\nUnder FCRA §605(c), re-aging an account to extend negative reporting is strictly prohibited. I respectfully request that the account be corrected to reflect the original DOFD or be removed entirely if outside the reporting window.\n\nDocumentation is enclosed. Please provide written confirmation of the resolution.",
    "Duplicate account on report": "I am writing to dispute a duplicate entry of the same account on my credit report. This account is listed more than once with identical or nearly identical details, which falsely inflates my total number of accounts and skews my credit standing.\n\nThe Fair Credit Reporting Act §611 requires information on consumer reports to be accurate and not misleading. I am requesting that the duplicate tradeline be removed so only one accurate entry remains.\n\nSupporting information is provided for your investigation.",
    "Account included in bankruptcy": "I am disputing the status of this account, which was legally discharged as part of my bankruptcy filing but is still being reported as active or delinquent. This reporting is inaccurate and violates my rights under federal bankruptcy law and credit reporting regulations.\n\nAccording to FCRA §1681c and bankruptcy guidelines, accounts included in bankruptcy must be updated to reflect their discharged status. I am requesting that this account be immediately corrected to show 'included in bankruptcy' and carry a zero balance.\n\nI’ve included documentation for your review.",
    "Fraudulent account": "I am disputing an account listed on my credit file that is the result of fraudulent activity. I did not open, authorize, or have any knowledge of this account until reviewing my credit report.\n\nAs provided under FCRA §605B and §623(a)(6), I am exercising my right to request removal of this unauthorized tradeline due to fraud. I have attached a copy of my identity verification and supporting materials to validate this claim.\n\nPlease delete this account and confirm the action in writing.",
    "I was not an authorized user": "I am disputing an account that inaccurately reports me as an authorized user. I was never added to this account by the primary account holder, nor have I had any involvement with this tradeline.\n\nAccording to the FCRA §611 and §623, reporting consumer information under incorrect authorization is prohibited. I am requesting immediate removal of this tradeline from my credit file.\n\nPlease complete your investigation and confirm the outcome in writing.",
    "Incorrect payment history": "I am disputing inaccuracies in the payment history reported for the account referenced above. The payment timeline contains errors that misrepresent my record and do not reflect the actual activity associated with this account.\n\nAs outlined under FCRA §611, consumers have the right to dispute any incorrect or incomplete information. I respectfully request a full investigation and correction of the payment history to ensure that only accurate and verified data remains on my credit file.\n\nAttached is supporting information. Please confirm any updates in writing.",
    "Account already paid or settled": "I am writing to dispute the reporting of an account that has already been fully paid or legally settled. Despite this, the account continues to reflect as open, past due, or delinquent, which is both inaccurate and harmful to my credit profile.\n\nUnder FCRA §623(a), furnishers are required to provide complete and correct information. I request that the account be updated to reflect a zero balance and a closed or settled status in line with the actual resolution.\n\nDocumentation supporting this payment or settlement is enclosed.",
    "Wrong account status reported": "I am disputing the status code currently associated with this account. It reflects a derogatory condition such as '120 days late' or 'charged-off' when this does not match my actual account history or any valid payment record.\n\nIn accordance with FCRA §611, I am requesting that the inaccurate status be fully verified and corrected to reflect the true condition of this account.\n\nI have included supporting documentation and look forward to your written confirmation of the update.",
    "Outdated account info (older than 7-10 years)": "I am requesting the removal of the referenced account based on its age. This negative item has exceeded the legal reporting limits under federal law and should no longer appear on my credit report.\n\nAs outlined in FCRA §605(a)(4)-(5), derogatory accounts must be removed after seven years from the original date of delinquency, and bankruptcies after ten years.\n\nPlease verify the age of the account and remove it accordingly. I appreciate your compliance with federal regulations.",
    "Charge-off account still updating monthly": "I am disputing the ongoing monthly updates to a charged-off account on my credit report. Once an account is charged off, it should not continue reporting new activity unless payments are being made. These updates may constitute re-aging, which is prohibited.\n\nUnder FCRA §605 and §623(a)(2), negative accounts must reflect accurate timelines. I request a review of this reporting activity and that it be corrected or removed if in violation.\n\nPlease investigate and provide written confirmation."
}

if submit:
    success = insert_dispute_submission(
        name, email, address, dob, ssn_last4, bureau,
        ", ".join(dispute_reasons), letter_date.strftime("%m/%d/%Y")
    )

    if success:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=12)

        pdf.multi_cell(0, 8, f"{name}\n{address}\n\n{email}\nDOB: {dob}\n")
        pdf.ln(1)
        pdf.multi_cell(0, 8, bureau_addresses[bureau])
        pdf.ln(1)
        for reason in dispute_reasons:
            if reason in letter_templates:
                pdf.multi_cell(0, 8, f"\n{letter_date.strftime('%B %d, %Y')}\n{letter_templates[reason]}\n")
                pdf.ln(1)
        pdf.multi_cell(0, 8, f"Account Name: {account_name}\nAccount Number: {account_number}\n")
        pdf.ln(1)
        pdf.multi_cell(0, 8, "I have attached identification and supporting documentation to validate this dispute. Please complete your investigation and provide a response in writing within the 30-day window as required under federal law.")
        pdf.ln(2)
        pdf.multi_cell(0, 8, "Thank you for your time and attention to this matter.")
        pdf.ln(2)
        pdf.multi_cell(0, 8, f"Sincerely,\n{name}\nSSN (Last 4 Digits): {ssn_last4}\nDOB: {dob}")

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
