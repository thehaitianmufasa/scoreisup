# Force rebuild to deploy waitlist live
import streamlit as st
import mysql.connector
from mysql.connector import IntegrityError
import requests
import smtplib
from email.mime.text import MIMEText
import logging

st.set_page_config(page_title="ScoreIsUp Waitlist", layout="centered")

# ----------- Email Config (SMTP) -----------
SMTP_HOST = "smtp.mailgun.org"
SMTP_PORT = 587
SMTP_USER = "postmaster@mg.scoreisup.com"
SMTP_PASS = "Paysoz991@#"
FROM_EMAIL = "ScoreIsUp <postmaster@mg.scoreisup.com>"

# Add a file handler for email debug logs (waitlist)
waitlist_email_logger = logging.getLogger("waitlist_email_debug")
waitlist_file_handler = logging.FileHandler("waitlist_email_debug.log")
waitlist_file_handler.setLevel(logging.INFO)
waitlist_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
waitlist_file_handler.setFormatter(waitlist_formatter)
if not waitlist_email_logger.hasHandlers():
    waitlist_email_logger.addHandler(waitlist_file_handler)
waitlist_email_logger.propagate = False

# ----------- Send Confirmation Email (SMTP) -----------
def send_confirmation_email(to_email):
    waitlist_email_logger.info(f"Starting waitlist confirmation email for {to_email}")
    waitlist_email_logger.info(f"SMTP_USER: {SMTP_USER}")
    
    msg = MIMEText(
        """Thank you for joining the ScoreIsUp waitlist!\n\nWe'll notify you when we are live — and thank you so much for the support.\n\n- Team ScoreIsUp"""
    )
    msg["Subject"] = "You're on the ScoreIsUp waitlist 🧠"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    try:
        waitlist_email_logger.info(f"Connecting to {SMTP_HOST}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            waitlist_email_logger.info("Connection established")
            waitlist_email_logger.info("Starting TLS...")
            server.starttls()
            waitlist_email_logger.info("TLS started")
            waitlist_email_logger.info(f"Logging in as {SMTP_USER}")
            server.login(SMTP_USER, SMTP_PASS)
            waitlist_email_logger.info("Login successful")
            waitlist_email_logger.info(f"Sending email to {to_email}")
            server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
            waitlist_email_logger.info("Email sent successfully!")
            return True
    except Exception as e:
        waitlist_email_logger.error(f"Error: {str(e)}")
        waitlist_email_logger.error(f"Error type: {type(e).__name__}")
        return False

# ----------- MySQL Connection -----------
def connect_db():
    return mysql.connector.connect(
        host="shortline.proxy.rlwy.net",
        port=59017,
        user="root",
        password="kAfGOGEepZaJkWdmTJpTSniVKBxUFNJy",
        database="railway"
    )

# ----------- Insert Email -----------
def insert_email(email):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO waitlist_users (email) VALUES (%s)", (email,))
        conn.commit()
        return True
    except IntegrityError:
        return False
    finally:
        conn.close()

# ----------- Main App -----------
def main():
    st.markdown(
        """
        <style>
        body {
          background-color: #0f0f0f;
        }
        .centered {
          text-align: center;
          margin-top: 100px;
          color: white;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .number {
          font-size: 3em;
          font-weight: bold;
          background: linear-gradient(to right, #5ea1ff, #6affc5);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='centered'>", unsafe_allow_html=True)
    st.title("You're on the ScoreIsUp Waitlist")
    st.markdown("**Enter your email to secure your spot.**")
    st.markdown("</div>", unsafe_allow_html=True)

    email = st.text_input("Email Address")

    if st.button("Join Waitlist"):
        if email:
            added = insert_email(email)
            if added:
                send_confirmation_email(email)
                st.success("🎉 You're officially on the waitlist. A confirmation email has been sent!")
            else:
                st.warning("You've already joined the waitlist.")
        else:
            st.error("Please enter a valid email.")

# ----------- Run -----------
if __name__ == "__main__":
    main()
