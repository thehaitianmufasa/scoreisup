import streamlit as st
import datetime

# Set page config
st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color Palette
primary = "#fdbb6d"
accent = "#e86b75"
success = "#5dc1ae"
purple = "#915ab7"
light_bg = "#f2f0f5"
dark = "#252e3e"

# Sidebar
with st.sidebar:
    st.markdown(f"""
        <style>
        .sidebar .sidebar-content {{
            background-color: {dark};
            color: white;
        }}
        </style>
    """, unsafe_allow_html=True)
    st.title("📊 Dashboard")
    st.markdown("---")
    st.subheader("Navigation")
    st.button("Home")
    st.button("Disputes")
    st.button("Reports")
    st.button("Settings")

# Header
st.markdown(f"""
    <h2 style='color:{dark}'>Welcome to Your Credit Dashboard</h2>
    <hr style='border: 1px solid {primary};'/>
""", unsafe_allow_html=True)

# Metric Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Disputes", "45", "+5", delta_color="normal")
col2.metric("Resolved", "32", "+2", delta_color="normal")
col3.metric("Pending", "13", "0", delta_color="off")
col4.metric("Success Rate", "71%", "+3%", delta_color="inverse")

# Charts Area
st.markdown("### 📈 Dispute Summary")
chart_col1, chart_col2 = st.columns([2, 1])
with chart_col1:
    st.line_chart({
        "Resolved": [5, 7, 8, 12, 18, 21, 32],
        "Pending": [20, 17, 14, 12, 11, 13, 13]
    })

with chart_col2:
    st.bar_chart({
        "Categories": ["ID Theft", "Late Payment", "Wrong Balance"],
        "Cases": [18, 12, 15]
    })

# Recent Activity / Table
st.markdown("### 📝 Recent Submissions")
st.table({
    "Date": ["2025-05-01", "2025-04-29", "2025-04-27"],
    "Account": ["Capital One", "Discover", "Chase"],
    "Status": ["Resolved", "Pending", "Resolved"]
})

# Footer / Note
st.markdown(f"""
    <div style='margin-top: 50px; padding: 10px; background-color: {light_bg}; border-left: 5px solid {primary};'>
        <strong>Tip:</strong> Always upload clear documentation to improve success rate.
    </div>
""", unsafe_allow_html=True)

