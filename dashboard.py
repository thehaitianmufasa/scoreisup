import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
# from ui_helpers import render_footer  # No longer needed

def random_recent_submissions(n=3):
    accounts = ["Capital One", "Discover", "Chase", "Amex", "Wells Fargo", "Citi"]
    statuses = ["Resolved", "Pending", "Resolved", "Resolved"]
    today = datetime.today()
    return [
        {
            "Date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            "Account": random.choice(accounts),
            "Status": random.choice(statuses)
        }
        for i in range(n)
    ]

def random_cases_and_categories():
    categories = ["ID Theft", "Late Payment", "Wrong Balance", "Duplicate Account", "Charge-Off"]
    return {
        "Categories": categories,
        "Cases": [random.randint(10, 30) for _ in categories]
    }

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

accounts = [
    "Wells Fargo", "Capital One", "Discover", "Chase", "Amex", "Citi", "Bank of America"
]
statuses = ["Resolved", "Pending", "In Progress"]

today = datetime.today()
start_date = today - timedelta(days=30)
data = []
for _ in range(3):
    date = random_date(start_date, today).strftime("%Y-%m-%d")
    account = random.choice(accounts)
    status = random.choice(statuses)
    data.append({"Date": date, "Account": account, "Status": status})

df = pd.DataFrame(data)

def show_dashboard():
    # Color Palette
    primary = "#fdbb6d"
    accent = "#e86b75"
    success = "#5dc1ae"
    purple = "#915ab7"
    light_bg = "#f2f0f5"
    dark = "#252e3e"

    # Header
    st.markdown(f"""
        <h2 style='color:{dark}'>Welcome to Your Credit Dashboard</h2>
        <hr style='border: 1px solid {primary};'/>
    """, unsafe_allow_html=True)

    st.markdown(f"## Welcome, {st.session_state.user_name}!")
    st.info("Tip: Always upload clear documentation to improve your dispute success rate.")

    # Metrics with BangoDash colors
    total_disputes = random.randint(40, 60)
    resolved = random.randint(30, total_disputes)
    pending = total_disputes - resolved
    success_rate = int((resolved / total_disputes) * 100)
    st.markdown("""
    <div style='display: flex; gap: 1.5rem; margin-bottom: 2rem;'>
        <div style='flex:1; background: #3b8beb; color: white; border-radius: 12px; padding: 1.5rem; text-align: center;'>
            <div style='font-size: 2.2rem; font-weight: bold;'>{}</div>
            <div style='font-size: 1.1rem;'>Total Disputes</div>
        </div>
        <div style='flex:1; background: #e14eca; color: white; border-radius: 12px; padding: 1.5rem; text-align: center;'>
            <div style='font-size: 2.2rem; font-weight: bold;'>{}</div>
            <div style='font-size: 1.1rem;'>Resolved</div>
        </div>
        <div style='flex:1; background: #fdcb6e; color: #23272b; border-radius: 12px; padding: 1.5rem; text-align: center;'>
            <div style='font-size: 2.2rem; font-weight: bold;'>{}</div>
            <div style='font-size: 1.1rem;'>Pending</div>
        </div>
        <div style='flex:1; background: #00b894; color: white; border-radius: 12px; padding: 1.5rem; text-align: center;'>
            <div style='font-size: 2.2rem; font-weight: bold;'>{}%</div>
            <div style='font-size: 1.1rem;'>Success Rate</div>
        </div>
    </div>
    """.format(total_disputes, resolved, pending, success_rate), unsafe_allow_html=True)

    # Our Community Table (replaces Recent Submissions)
    st.markdown("## 🧑‍🤝‍🧑 Our Community")
    st.table(df)

    # Footer Tip Box
    st.markdown(f"""
        <div style='margin-top: 50px; padding: 10px; background-color: {light_bg}; border-left: 5px solid {primary};'>
            <strong>Tip:</strong> Always upload clear documentation to improve success rate.
        </div>
    """, unsafe_allow_html=True)

    # Cohesive 3-button row at the bottom
    st.markdown("---")
    bcol1, bcol2, bcol3 = st.columns(3)
    with bcol1:
        if st.button("Start a New Dispute"):
            st.session_state["nav"] = "Dispute Letter"
            st.rerun()
    with bcol2:
        st.link_button("Check Credit Report", "https://www.annualcreditreport.com/index.action")
    with bcol3:
        st.link_button("CFPB Dispute Portal", "https://www.consumerfinance.gov/complaint/")

    # Footer removed; handled by app.py
