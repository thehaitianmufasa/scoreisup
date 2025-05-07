
import streamlit as st

if "dispute_reset" not in st.session_state:
    st.session_state["dispute_reset"] = True
    st.session_state["Select Dispute Reason(s)"] = []

from fpdf import FPDF
import tempfile

st.title("📄 Credit Dispute Letter Generator")

# --- Input Form ---

with st.form("dispute_form"):
    client_name = st.text_input("Full Name")
    account_name = st.text_input("Account Name")
    account_number = st.text_input("Account Number (e.g., xxx-8592)")
    address = st.text_input("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)")

    import datetime
    letter_date = st.date_input("Select Letter Date", value=datetime.date.today())

    email = st.text_input("Email Address")
    ssn_last4 = st.text_input("Last 4 Digits of SSN")

    bureau_options = {
        "Equifax": "Equifax Security & Fraud Prevention
P.O. Box 105788
Atlanta, GA 30348-5788",
        "Experian": "Experian Consumer Disputes
P.O. Box 4500
Allen, TX 75013",
        "TransUnion": "TransUnion Consumer Solutions
P.O. Box 2000
Chester, PA 19016"
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


# --- Text Blocks for Each Dispute Reason ---
reason_texts = {
    "Account not mine (identity theft)": (
        "Urgent Request to Remove Fraudulent Account from Credit Report",
        """I am writing to formally dispute an account appearing on my credit report that I did not authorize or open. After reviewing my credit file, I discovered this account, which is the result of identity theft. I did not apply for, open, or use this account in any capacity, nor have I ever had a relationship with the creditor associated with it.

Under my rights granted by the Fair Credit Reporting Act (FCRA), specifically §605B and §609(a), I request the immediate deletion of this fraudulent account from my credit profile. I have included proper identification and supporting documentation to validate my claim.

Please investigate this matter and confirm deletion in writing."""
    ),
    "Paid account still showing unpaid": (
        "Dispute Regarding Paid Account Still Reporting as Unpaid",
        """I am writing to dispute the inaccurate reporting of an account that has been fully paid yet continues to appear as unpaid on my credit report. I have satisfied the balance in full, and this continued misreporting is damaging and misleading.

Under the Fair Credit Reporting Act (FCRA) §623(a)(2), furnishers are required to update and correct any inaccurate or incomplete information they provide. I respectfully request immediate correction of this account status to reflect its paid nature.

Supporting documentation is enclosed. Please investigate and confirm the update in writing."""
    ),
    "Never late but marked late": (
        "Request to Correct False Late Payment Reporting",
        """I am disputing the accuracy of reported late payments associated with this account. I have never missed or submitted a late payment, and my records reflect consistent, on-time activity throughout the life of this account.

Reporting false delinquencies constitutes a violation under FCRA §611 and causes undue harm to my credit profile. I request that you investigate this entry, verify the payment history, and remove any inaccurate notations from my report.

I have included evidence and supporting records for your review."""
    ),
    "Balance is incorrect": (
        "Incorrect Balance Dispute on Reported Account",
        """I am formally disputing the balance currently reported for the account listed above. The figure does not accurately reflect the amount owed, paid, or settled. This discrepancy may be due to reporting delays or data entry errors, but it must be corrected.

Pursuant to FCRA §611, I request that the reporting furnisher verify the correct balance and promptly update the credit file to reflect the accurate amount.

Please find supporting documentation attached. I appreciate your cooperation in resolving this matter."""
    ),
    "Account was settled but shows as charged-off": (
        "Dispute Regarding Settled Account Incorrectly Marked as Charged-Off",
        """I am disputing the current status of this account, which inaccurately reports as charged-off despite being settled. I negotiated and completed a settlement agreement with the creditor, and as such, the status should reflect 'settled' rather than 'charged-off.'

Under FCRA §623(a), creditors are legally obligated to report information accurately and fairly. I respectfully request that the tradeline be corrected to show the true status.

Attached are relevant documents supporting the settlement. Please investigate and amend accordingly."""
    ),
    "Re-aged account / illegally reset": (
        "Dispute of Re-aged Account in Violation of Federal Law",
        """I am disputing the reporting of an account that appears to have been re-aged in violation of federal credit reporting laws. The date of first delinquency (DOFD) should remain fixed, yet this account continues to reflect an updated or extended timeline that inaccurately prolongs its presence on my report.

Under FCRA §605(c), re-aging an account to extend negative reporting is strictly prohibited. I respectfully request that the account be corrected to reflect the original DOFD or be removed entirely if outside the reporting window.

Documentation is enclosed. Please provide written confirmation of the resolution."""
    ),
    "Duplicate account on report": (
        "Dispute of Duplicate Account Entry on Credit Report",
        """I am writing to dispute a duplicate entry of the same account on my credit report. This account is listed more than once with identical or nearly identical details, which falsely inflates my total number of accounts and skews my credit standing.

The Fair Credit Reporting Act §611 requires information on consumer reports to be accurate and not misleading. I am requesting that the duplicate tradeline be removed so only one accurate entry remains.

Supporting information is provided for your investigation."""
    ),
    "Account included in bankruptcy": (
        "Dispute of Bankruptcy-Related Account Reporting",
        """I am disputing the status of this account, which was legally discharged as part of my bankruptcy filing but is still being reported as active or delinquent. This reporting is inaccurate and violates my rights under federal bankruptcy law and credit reporting regulations.

According to FCRA §1681c and bankruptcy guidelines, accounts included in bankruptcy must be updated to reflect their discharged status. I am requesting that this account be immediately corrected to show 'included in bankruptcy' and carry a zero balance.

I’ve included documentation for your review."""
    ),
    "Fraudulent account": (
        "Urgent Dispute - Fraudulent Account Reporting",
        """I am disputing an account listed on my credit file that is the result of fraudulent activity. I did not open, authorize, or have any knowledge of this account until reviewing my credit report.

As provided under FCRA §605B and §623(a)(6), I am exercising my right to request removal of this unauthorized tradeline due to fraud. I have attached a copy of my identity verification and supporting materials to validate this claim.

Please delete this account and confirm the action in writing."""
    ),
    "I was not an authorized user": (
        "Dispute – Inaccurate Authorized User Status",
        """I am disputing an account that inaccurately reports me as an authorized user. I was never added to this account by the primary account holder, nor have I had any involvement with this tradeline.

According to the FCRA §611 and §623, reporting consumer information under incorrect authorization is prohibited. I am requesting immediate removal of this tradeline from my credit file.

Please complete your investigation and confirm the outcome in writing."""
    ),
    "Incorrect payment history": (
        "Request for Correction of Inaccurate Payment History",
        """I am disputing inaccuracies in the payment history reported for the account referenced above. The payment timeline contains errors that misrepresent my record and do not reflect the actual activity associated with this account.

As outlined under FCRA §611, consumers have the right to dispute any incorrect or incomplete information. I respectfully request a full investigation and correction of the payment history to ensure that only accurate and verified data remains on my credit file.

Attached is supporting information. Please confirm any updates in writing."""
    ),
    "Account already paid or settled": (
        "Dispute of Account Reported as Unpaid Despite Settlement",
        """I am writing to dispute the reporting of an account that has already been fully paid or legally settled. Despite this, the account continues to reflect as open, past due, or delinquent, which is both inaccurate and harmful to my credit profile.

Under FCRA §623(a), furnishers are required to provide complete and correct information. I request that the account be updated to reflect a zero balance and a closed or settled status in line with the actual resolution.

Documentation supporting this payment or settlement is enclosed."""
    ),
    "Wrong account status reported": (
        "Correction Request for Wrong Account Status",
        """I am disputing the status code currently associated with this account. It reflects a derogatory condition such as '120 days late' or 'charged-off' when this does not match my actual account history or any valid payment record.

In accordance with FCRA §611, I am requesting that the inaccurate status be fully verified and corrected to reflect the true condition of this account.

I have included supporting documentation and look forward to your written confirmation of the update."""
    ),
    "Outdated account info (older than 7-10 years)": (
        "Request for Removal of Outdated Account Information",
        """I am requesting the removal of the referenced account based on its age. This negative item has exceeded the legal reporting limits under federal law and should no longer appear on my credit report.

As outlined in FCRA §605(a)(4)-(5), derogatory accounts must be removed after seven years from the original date of delinquency, and bankruptcies after ten years.

Please verify the age of the account and remove it accordingly. I appreciate your compliance with federal regulations."""
    ),
    "Charge-off account still updating monthly": (
        "Illegal Re-aging of Charged-Off Account",
        """I am disputing the ongoing monthly updates to a charged-off account on my credit report. Once an account is charged off, it should not continue reporting new activity unless payments are being made. These updates may constitute re-aging, which is prohibited.

Under FCRA §605 and §623(a)(2), negative accounts must reflect accurate timelines. I request a review of this reporting activity and that it be corrected or removed if in violation.

Please investigate and provide written confirmation."""
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
        f"Sincerely,\n{client_name}\nSSN (Last 4 Digits): {ssn_last4}\nDOB: {dob}"
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

# 🔗 Free Credit Report Button
st.markdown("### 🔍 Get Your Free Weekly Credit Report")
st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")


    send_email_with_attachment(email, tmp_path)