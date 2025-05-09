import streamlit as st
import os as os_module  # SAFE alias for os

st.title("✅ OS Sanity Check (Aliased)")

font_path = "DejaVuSans.ttf"

st.write("Checking font path:", font_path)

# Confirm we're using the correct os
st.write("os_module is a module:", hasattr(os_module, "path"))

try:
    exists = os_module.path.exists(font_path)
    st.success(f"Font file exists: {exists}")
except Exception as e:
    st.error(f"ERROR using os_module.path.exists(): {e}")
