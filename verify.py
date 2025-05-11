import streamlit as st
from db import get_user_by_email, get_connection

def verify_user(email, token):
    user = get_user_by_email(email)
    if not user:
        return False, "User not found."
    if user.get("verified"):
        return False, "Your email is already verified."
    if user.get("verification_token") != token:
        return False, "Invalid or expired verification link."
    # Mark user as verified
    try:
        conn = get_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET verified = %s, verification_token = NULL WHERE email = %s",
                (True, email)
            )
            conn.commit()
            cursor.close()
            conn.close()
        return True, "Your email has been verified! You can now log in."
    except Exception as e:
        return False, f"Verification failed: {str(e)}"

st.set_page_config(page_title="Email Verification | ScoreIsUp")
st.markdown("# Email Verification")

params = st.query_params
email = params.get("email", [None])[0]
token = params.get("token", [None])[0]

if not email or not token:
    st.error("Invalid verification link.")
else:
    success, message = verify_user(email, token)
    if success:
        st.success(message)
    else:
        st.error(message) 