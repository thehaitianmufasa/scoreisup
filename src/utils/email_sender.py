
import smtplib
import os
from email.message import EmailMessage

def send_email(to_email, subject, content):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ.get("SMTP_USER")
    msg["To"] = to_email
    msg.set_content(content)

    with smtplib.SMTP(os.environ.get("SMTP_HOST"), int(os.environ.get("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
        server.send_message(msg)
