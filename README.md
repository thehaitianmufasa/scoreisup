# 🧾 Dispute Letter Generator (Streamlit App)

This Streamlit application allows users to generate legally structured dispute letters for credit bureaus based on a selection of predefined dispute reasons.

## 🚀 Features
- Select one or more dispute reasons from a legal mapping.
- Input personal info and account details.
- Auto-generates a PDF letter addressed to the chosen credit bureau.
- Fully browser-based (no install required if deployed on Streamlit Cloud).

## 🛠️ How to Run Locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🌐 Or Deploy on Streamlit Cloud
1. Push this repo to GitHub.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and link your GitHub.
3. Choose `streamlit_app.py` as the entry point.
4. Deploy and share your URL!

## 📄 Dependencies
- [streamlit](https://docs.streamlit.io/)
- [fpdf](https://pyfpdf.readthedocs.io/)

## 📬 Example Use Case
Generate a letter like:
> "Re: Incorrect Balance & Duplicate Account on Report"  
> Sent to Experian with your name, address, and SSN included in the signature block.

