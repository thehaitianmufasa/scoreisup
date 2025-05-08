import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
from db import insert_dispute_submission

st.title("📄 Credit Dispute Letter Generator")

# --- Session State for Multiple Accounts ---
if "num_accounts" not in st.session_state:
    st.session_state.num_accounts = 1

def add_account():
    if st.session_state.num_accounts < 5:
        st.session_state.num_accounts += 1

# --- Add Account Button (OUTSIDE the form) ---
if st.session_state.num_accounts < 5:
    if st.button("➕ Add Another Account"):
        add_account()

# --- Form ---
with st.form("dispute_form"):
    st.markdown("## 🔒 Your Information")
    client_name = st.text_input("Full Name")
    address = st.text_input("Mailing Address")
    dob = st.text_input("Date of Birth (MM/DD/YYYY)", help="Used to match your identity during bureau review.")
    letter_date = st.date_input("Select Letter Date", value=datetime.date.today())
    email = st.text_input("Email Address")
    ssn_last4 = st.text_input("Last 4 Digits of SSN", help="Only used for ID verification in your dispute letter.")

    st.markdown("## 🏢 Choose Credit Bureau")
    bureau_options = {
        "Equifax": "Equifax Security & Fraud Prevention\nP.O. Box 105788\nAtlanta, GA 30348-5788",
        "Experian": "Experian Consumer Disputes\nP.O. Box 4500\nAllen, TX 75013",
        "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016"
    }
    selected_bureau = st.selectbox("Credit Bureau", list(bureau_options.keys()))

    st.markdown("## 🧾 Account(s) You're Disputing")

    # Add Another Account button (inside form for better layout)
    if st.session_state.num_accounts < 5:
        st.form_submit_button("➕ Add Another Account", on_click=add_account, key="add_account_button")

    account_fields = []
    for i in range(st.session_state.num_accounts):
        st.markdown(f"### 📄 Account #{i+1}")
        cols = st.columns([1, 1])
        with cols[0]:
            acct_name = st.text_input(f"Account Name {i+1}", key=f"acct_name_{i}")
        with cols[1]:
            acct_number = st.text_input(f"Account Number {i+1}", key=f"acct_number_{i}")
        account_fields.append((acct_name, acct_number))

    st.markdown("## ⚖️ Reason(s) for Dispute")
    dispute_options = [
        'Account not mine (identity theft)', 'Paid account still showing unpaid',
        'Never late but marked late', 'Balance is incorrect',
        'Account was settled but shows as charged-off', 'Re-aged account / illegally reset',
        'Duplicate account on report', 'Account included in bankruptcy',
        'Fraudulent account', 'I was not an authorized user',
        'Incorrect payment history', 'Account already paid or settled',
        'Wrong account status reported', 'Outdated account info (older than 7-10 years)',
        'Charge-off account still updating monthly'
    ]
    selected_reasons = st.multiselect("Select Reason(s)", dispute_options)

    submitted = st.form_submit_button("📄 Generate Dispute Letter")


# --- Generate Letter ---
if submitted and selected_reasons:
    subject_line = "Re: " + " & ".join([reason_texts[r][0] for r in selected_reasons])
    combined_body = ""
    for reason in selected_reasons:
        combined_body += reason_texts[reason][1] + "\n\n"

    account_section = "\n".join([
        f"Account Name: {name}\nAccount Number: {number}\n"
        for name, number in account_fields if name and number
    ])

    sections = [
        f"{client_name}\n{address}\n{email}\nDOB: {dob}\n",
        bureau_options[selected_bureau],
        f"\n{subject_line}\n",
        "Dear Sir/Madam,\n",
        combined_body.strip(),
        account_section,
        "I have attached identification and supporting documentation to validate this dispute. "
        "Please complete your investigation and provide a response in writing within the 30-day window as required under federal law.",
        "Thank you for your time and attention to this matter.",
        f"Sincerely,\n{client_name}\nSSN (Last 4 Digits): {ssn_last4}\nDOB: {dob}\nDate: {letter_date.strftime('%B %d, %Y')}"
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

    # Save to MySQL
    insert_dispute_submission(
        client_name, email, address, dob, ssn_last4,
        selected_bureau,
        ", ".join(selected_reasons),
        letter_date
    )

    with open(tmp_path, "rb") as f:
        st.download_button("📥 Download Your Dispute Letter", f, file_name="dispute_letter.pdf")

st.markdown("### 🔍 Get Your Free Weekly Credit Report")
st.link_button("Visit AnnualCreditReport.com", "https://www.annualcreditreport.com/index.action")

