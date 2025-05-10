import streamlit as st
import bcrypt
from db import get_user_by_email, insert_user
import time
import smtplib
from email.mime.text import MIMEText
import uuid
import os
import json
from datetime import datetime, timedelta

# In-memory rate limiting store
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 300  # 5 minutes
RATE_LIMIT_MAX_ATTEMPTS = 5

# SMTP settings from environment variables
MAILGUN_SMTP_HOST = os.getenv('MAILGUN_SMTP_HOST', 'smtp.mailgun.org')
MAILGUN_SMTP_PORT = int(os.getenv('MAILGUN_SMTP_PORT', '587'))
MAILGUN_SMTP_USER = os.getenv('MAILGUN_SMTP_USER', 'postmaster@mg.scoreisup.com')
MAILGUN_SMTP_PASS = os.getenv('MAILGUN_SMTP_PASS', 'Paysoz991@#')

# Session management
def init_session():
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()

def check_session():
    """Check if user is logged in and session is valid"""
    if st.session_state.logged_in and st.session_state.user_email:
        # Update last activity
        st.session_state.last_activity = datetime.now()
        return True
    return False

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
        stored_hash = user.get("password")
        if not stored_hash:
            st.error("Account error: No password hash found. Please contact support.")
            return
        try:
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = stored_hash.encode('utf-8')
            if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                # Set session state
                st.session_state.logged_in = True
                st.session_state.user_email = user["email"]
                st.session_state.last_activity = datetime.now()
                st.success(f"Welcome back, {user['email']}!")
                st.rerun()
            else:
                st.error("Invalid email or password.")
                record_attempt(ip, 'login')
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")
            record_attempt(ip, 'login')

def logout():
    """Logout user and clear session"""
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.last_activity = None
    st.rerun()

def get_app_domain():
    """Get the current application domain"""
    try:
        # Try to get from Streamlit headers
        if hasattr(st, 'request') and st.request.headers:
            return st.request.headers.get('Host', 'scoreisup.com')
        # Try to get from environment variable
        return os.getenv('APP_DOMAIN', 'scoreisup.com')
    except Exception:
        return 'scoreisup.com'

def send_verification_email(email, token):
    """Send verification email to user"""
    try:
        # Get the current domain
        current_domain = get_app_domain()
        verify_link = f"https://{current_domain}/verify?email={email}&token={token}"
        
        # Log the attempt
        print(f"Attempting to send verification email to {email}")
        print(f"Using domain: {current_domain}")
        print(f"Verification link: {verify_link}")
        
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
        
        # Test SMTP connection first
        with smtplib.SMTP(MAILGUN_SMTP_HOST, MAILGUN_SMTP_PORT) as server:
            server.starttls()
            server.login(MAILGUN_SMTP_USER, MAILGUN_SMTP_PASS)
            server.sendmail(msg["From"], [email], msg.as_string())
            
        print(f"✅ Verification email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication failed: {str(e)}"
        print(error_msg)
        st.error("Email service configuration error. Please contact support.")
        return False
        
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error occurred: {str(e)}"
        print(error_msg)
        st.error("Failed to send verification email. Please try again.")
        return False
        
    except Exception as e:
        error_msg = f"Unexpected error sending verification email: {str(e)}"
        print(error_msg)
        st.error("An unexpected error occurred. Please try again or contact support.")
        return False

def send_welcome_email(email):
    """Send welcome email to user"""
    try:
        body = f"""
Hi {email.split('@')[0].title()},

🎉 Welcome to ScoreIsUp!

Thank you for signing up. You can now log in and start using our credit tools.

— The ScoreIsUp Team
"""
        msg = MIMEText(body)
        msg["Subject"] = "Welcome to ScoreIsUp!"
        msg["From"] = "ScoreIsUp <no-reply@scoreisup.com>"
        msg["To"] = email
        
        with smtplib.SMTP(MAILGUN_SMTP_HOST, MAILGUN_SMTP_PORT) as server:
            server.starttls()
            server.login(MAILGUN_SMTP_USER, MAILGUN_SMTP_PASS)
            server.sendmail(msg["From"], [email], msg.as_string())
            print(f"✅ Welcome email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Failed to send welcome email: {str(e)}")
        return False

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
            if insert_user(email, password, verified=True):
                send_welcome_email(email)
                # Set session state
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.last_activity = datetime.now()
                st.success("Account created successfully! You can now log in.")
                st.rerun()
            else:
                st.error("Failed to create account. Please try again.")
                record_attempt(ip, 'signup')
        except Exception as e:
            st.error(f"Error creating account: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")
            record_attempt(ip, 'signup')

def test_email_sending():
    """Test function to verify email sending functionality"""
    test_email = "thejeffchery@gmail.com"  # Using the provided email
    # Get the actual token from the database
    user = get_user_by_email(test_email)
    if not user:
        print("User not found in database")
        return False
    test_token = user.get("verification_token")
    if not test_token:
        print("No verification token found for user")
        return False
        
    try:
        print("Testing email configuration:")
        print(f"SMTP Host: {MAILGUN_SMTP_HOST}")
        print(f"SMTP Port: {MAILGUN_SMTP_PORT}")
        print(f"SMTP User: {MAILGUN_SMTP_USER}")
        print("SMTP Pass: [REDACTED]")
        
        with smtplib.SMTP(MAILGUN_SMTP_HOST, MAILGUN_SMTP_PORT) as server:
            server.starttls()
            server.login(MAILGUN_SMTP_USER, MAILGUN_SMTP_PASS)
            print("SMTP connection and login successful!")
            
        # Try sending a test email
        send_verification_email(test_email, test_token)
        return True
    except Exception as e:
        print(f"Email test failed: {str(e)}")
        return False

# Initialize session at module level
init_session()

# Add this at the end of the file
if __name__ == "__main__":
    test_email_sending()

