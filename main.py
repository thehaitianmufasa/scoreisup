# Force rebuild to deploy waitlist live
import streamlit as st
import mysql.connector
from mysql.connector import IntegrityError
import requests

st.set_page_config(page_title="ScoreIsUp Waitlist", layout="centered")

# ----------- Mailgun Config -----------
MAILGUN_DOMAIN = "mg.scoreisup.com"
MAILGUN_API_KEY = "MAILGUN_API_KEY"
FROM_EMAIL = "ScoreIsUp <postmaster@mg.scoreisup.com>"

# ----------- Send Confirmation Email -----------
def send_confirmation_email(to_email):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": "You're on the ScoreIsUp waitlist 🧠",
            "text": (
                "Thank you for joining!\n\n"
                "We’ll notify you when we are live — and thank you so much for the support.\n\n"
                "- Team ScoreIsUp"
            )
        }
    )

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
                st.warning("You’ve already joined the waitlist.")
        else:
            st.error("Please enter a valid email.")

# ----------- Run -----------
if __name__ == "__main__":
    main()
