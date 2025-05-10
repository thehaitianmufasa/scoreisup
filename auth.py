import streamlit as st
import bcrypt
from db import get_user_by_email, insert_user
import time
import smtplib
from email.mime.text import MIMEText
import uuid

# In-memory rate limiting store
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 300  # 5 minutes
RATE_LIMIT_MAX_ATTEMPTS = 5

MAILGUN_SMTP_HOST = "smtp.mailgun.org"
MAILGUN_SMTP_PORT = 587
MAILGUN_SMTP_USER = "postmaster@mg.scoreisup.com"
MAILGUN_SMTP_PASS = "Paysoz991@#"

def get_client_ip():
    # Try to get IP from Streamlit headers (works if behind a proxy)
    ip = st.query_params.get('ip', [None])[0]
    if not ip:
        ip = st.request.headers.get('X-Forwarded-For', None) if hasattr(st, 'request') else None
    if not ip:
        ip = 'local'  # fallback for local testing
    return ip

def is_rate_limited(ip, action):
    now = time.time()
    key = f"{ip}:{action}"
    attempts = RATE_LIMIT.get(key, [])
    # Remove old attempts
    attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW]
    RATE_LIMIT[key] = attempts
    if len(attempts) >= RATE_LIMIT_MAX_ATTEMPTS:
        return True
    return False

def record_attempt(ip, action):
    now = time.time()
    key = f"{ip}:{action}"
    attempts = RATE_LIMIT.get(key, [])
    attempts.append(now)
    RATE_LIMIT[key] = attempts

def login():
    st.markdown("## 🔐 Login")
    ip = get_client_ip()
    if is_rate_limited(ip, 'login'):
        st.error("Too many login attempts. Please try again later.")
        return
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    # Simple CAPTCHA
    captcha_answer = st.text_input("What is 3 + 4? (Anti-bot check)")
    if st.button("Login"):
        if not email or not password:
            st.error("Please enter both email and password.")
            return
        if captcha_answer.strip() != "7":
            st.error("CAPTCHA failed. Please answer the question correctly.")
            record_attempt(ip, 'login')
            return
        user = get_user_by_email(email)
        if not user:
            st.error("Invalid email or password.")
            record_attempt(ip, 'login')
            return
        if not user.get("verified"):
            st.error("Your email is not verified. Please check your inbox and click the verification link.")
            return
        stored_hash = user.get("password")
        if not stored_hash:
            st.error("Account error: No password hash found. Please contact support.")
            return
        try:
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = stored_hash.encode('utf-8')
            if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                st.session_state.logged_in = True
                st.session_state.user_email = user["email"]
                st.success(f"Welcome back, {user['email']}!")
                st.rerun()
            else:
                st.error("Invalid email or password.")
                record_attempt(ip, 'login')
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")
            record_attempt(ip, 'login')

def send_verification_email(email, token):
    verify_link = f"https://scoreisup.com/verify?email={email}&token={token}"
    body = f"""
Hi {email.split('@')[0].title()},

🎉 Welcome to ScoreIsUp!

Please verify your email by clicking the link below:
{verify_link}

If you didn't sign up, feel free to ignore this email.

— The ScoreIsUp Team
"""
    msg = MIMEText(body)
    msg["Subject"] = "Welcome to ScoreIsUp! Please verify your email"
    msg["From"] = "ScoreIsUp <no-reply@scoreisup.com>"
    msg["To"] = email
    try:
        with smtplib.SMTP(MAILGUN_SMTP_HOST, MAILGUN_SMTP_PORT) as server:
            server.starttls()
            server.login(MAILGUN_SMTP_USER, MAILGUN_SMTP_PASS)
            server.sendmail(msg["From"], [email], msg.as_string())
    except Exception as e:
        st.error(f"Failed to send verification email: {e}")

def signup():
    st.markdown("## ✍️ Sign Up")
    ip = get_client_ip()
    if is_rate_limited(ip, 'signup'):
        st.error("Too many sign up attempts. Please try again later.")
        return
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
    # Simple CAPTCHA
    captcha_answer = st.text_input("What is 5 + 2? (Anti-bot check)", key="signup_captcha")
    if st.button("Sign Up"):
        if not email or not password or not confirm_password:
            st.error("Please fill in all fields.")
            return
        if captcha_answer.strip() != "7":
            st.error("CAPTCHA failed. Please answer the question correctly.")
            record_attempt(ip, 'signup')
            return
        if password != confirm_password:
            st.error("Passwords do not match!")
            return
        if len(password) < 8:
            st.error("Password must be at least 8 characters long.")
            return
        user = get_user_by_email(email)
        if user:
            st.error("Email already exists!")
            record_attempt(ip, 'signup')
            return
        try:
            verification_token = str(uuid.uuid4())
            if insert_user(email, password, verification_token):
                send_verification_email(email, verification_token)
                st.success("Account created! Please check your email to verify your account before logging in.")
            else:
                st.error("Failed to create account. Please try again.")
                record_attempt(ip, 'signup')
        except Exception as e:
            st.error(f"Error creating account: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")
            record_attempt(ip, 'signup')

