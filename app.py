import streamlit as st
import os as os_module  # ✅ Protect against name collisions

st.title("🔍 OS Debugger (Safe Version)")

# Test the os module safely
st.write("✅ type of os_module:", type(os_module))
st.write("✅ hasattr(os_module, 'path'):", hasattr(os_module, "path"))
st.write("✅ repr of os_module:", repr(os_module))

# Check if font file exists
font_path = "DejaVuSans.ttf"
try:
    exists = os_module.path.exists(font_path)
    st.success(f"✅ os_module.path.exists('{font_path}') = {exists}")
except Exception as e:
    st.error(f"❌ os_module.path.exists threw error: {e}")
