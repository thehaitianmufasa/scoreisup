from fpdf import FPDF

# --- Full Dispute Mapping ---
# (Only the placeholder of dispute_mapping shown here for brevity; it would be complete in actual file)
dispute_mapping = {
    "Account not mine (identity theft)": {
        "subject": "Re: Urgent Request to Remove Fraudulent Account from Credit Report",
        "body": """I am writing to formally dispute an account appearing on my credit report that I did not authorize or open. After reviewing my credit file, I discovered this account, which is the result of identity theft. I did not apply for, open, or use this account in any capacity, nor have I ever had a relationship with the creditor associated with it.

Under my rights granted by the Fair Credit Reporting Act (FCRA), specifically §605B and §609(a), I request the immediate deletion of this fraudulent account from my credit profile. I have included proper identification and supporting documentation to validate my claim.

Please investigate this matter and confirm deletion in writing."""
    }
    # The rest of the categories would go here...
}

# Credit Bureau addresses
bureau_addresses = {
    "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
    "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
    "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
}

# 📎 User Inputs
client_name = input("Enter your full name: ")
account_name = input("Enter the account name: ")
account_number = input("Enter the account number (e.g., xxx-8592): ")
address = input("Enter your mailing address: ")
dob = input("Enter your date of birth (MM/DD/YYYY): ")
email = input("Enter your email address: ")
ssn_last4 = input("Enter the last 4 digits of your SSN: ")

print("\nChoose the credit bureau:")
bureau_options = list(bureau_addresses.keys())
for idx, name in enumerate(bureau_options):
    print(f"{idx + 1}. {name}")

try:
    bureau_choice = int(input("Enter the number of the bureau: ")) - 1
    selected_bureau = bureau_options[bureau_choice]
except (ValueError, IndexError):
    print("Invalid selection. Defaulting to Equifax.")
    selected_bureau = "Equifax"

# 🕓 Multiple Dispute Reasons
print("\nSelect dispute reason numbers separated by commas (e.g. 1,4,7):")
derogatory_options = list(dispute_mapping.keys())
for idx, option in enumerate(derogatory_options):
    print(f"{idx + 1}. {option}")

try:
    choices = input("Enter your choices: ").split(',')
    selected_reasons = [derogatory_options[int(c.strip()) - 1] for c in choices if c.strip().isdigit() and 0 < int(c.strip()) <= len(derogatory_options)]
except Exception:
    selected_reasons = ["Account not mine (identity theft)"]

# 📄 Build Dispute Letter
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

# 🔊 Generate PDF
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Helvetica", size=12)

for section in letter_sections:
    for line in section.strip().split("\n"):
        pdf.multi_cell(0, 8, line.strip())
    pdf.ln(4)

pdf.output("dispute_letter.pdf")

# 🥷 Download or Notify
try:
    from google.colab import files
    files.download("dispute_letter.pdf")
except ImportError:
    print("\n📅 PDF saved as 'dispute_letter.pdf'. Please open it from your working directory.")
