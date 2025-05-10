import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional
from src.utils.config import EMAIL_CONFIG

class EmailSender:
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG['SMTP_SERVER']
        self.smtp_port = EMAIL_CONFIG['SMTP_PORT']
        self.username = EMAIL_CONFIG['SMTP_USERNAME']
        self.password = EMAIL_CONFIG['SMTP_PASSWORD']
        self.from_email = EMAIL_CONFIG['FROM_EMAIL']

    def send_dispute_letter(
        self,
        to_email: str,
        subject: str,
        body: str,
        pdf_path: Optional[str] = None,
        cc: Optional[List[str]] = None
    ) -> bool:
        """
        Send a dispute letter via email with optional PDF attachment
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Add PDF attachment if provided
            if pdf_path:
                with open(pdf_path, 'rb') as f:
                    pdf = MIMEApplication(f.read(), _subtype='pdf')
                    pdf.add_header('Content-Disposition', 'attachment', filename='dispute_letter.pdf')
                    msg.attach(pdf)

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                # Send email
                recipients = [to_email] + (cc or [])
                server.sendmail(self.from_email, recipients, msg.as_string())
                
            return True

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def send_confirmation(
        self,
        to_email: str,
        letter_details: dict
    ) -> bool:
        """
        Send a confirmation email to the user
        """
        subject = "Your Dispute Letter Has Been Sent"
        body = f"""
        Dear {letter_details.get('name', 'User')},

        Your dispute letter has been successfully sent to {letter_details.get('bureau', 'the credit bureau')}.

        Letter Details:
        - Date Sent: {letter_details.get('date', 'N/A')}
        - Reference Number: {letter_details.get('reference', 'N/A')}
        - Dispute Reasons: {', '.join(letter_details.get('reasons', []))}

        If you have any questions, please don't hesitate to contact us.

        Best regards,
        ScoreIsUp Team
        """

        return self.send_dispute_letter(to_email, subject, body) 