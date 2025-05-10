import streamlit as st

# Dummy user for testing
DUMMY_USER = {
    "email": "test@example.com",
    "password": "Test@123"  # This is a simple password for testing
}

def login():
    st.markdown("## 🔐 Login")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if email == DUMMY_USER["email"] and password == DUMMY_USER["password"]:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid login credentials.")

def signup():
    st.markdown("## ✍️ Sign Up")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
            return
            
        if email == DUMMY_USER["email"]:
            st.error("Email already exists!")
            return
            
        # For testing, we'll just show a success message
        st.success("Account created successfully! You can now login.")
        st.info("For testing, use these credentials:\nEmail: test@example.com\nPassword: Test@123")

