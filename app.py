import streamlit as st
import os

st.title("🔍 OS Debugger")

# Check what 'os' is right now
st.write("✅ type of os:", type(os))
st.write("✅ hasattr(os, 'path'):", hasattr(os, "path"))
st.write("✅ repr of os:", repr(os))

# Safe test for file existence
font_path = "DejaVuSans.ttf"
try:
    exists = os.path.exists(font_path)
    st.success(f"✅ os.path.exists('{font_path}') = {exists}")
except Exception as e:
    st.error(f"❌ os.path.exists threw error: {e}")

