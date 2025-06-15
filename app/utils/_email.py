import os
import smtplib

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


class EmailSender:
    """Class to handle email sending functionality"""
    SUBJECT_INFO_TYPE = "Bet Builder - Info"
    SUBJECT_ERROR_TYPE = "Bet Builder - Error"

    def __init__(self, from_email: str, password: str):
        self.from_email = from_email
        self.password = password

        self.server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        self.server.login(from_email, password)

        self.message = MIMEMultipart("alternative")
        self.message["From"] = from_email

    def get_new_message(self, subject: str, to_email: str, body: str) -> None:
        """Create a new email message with the given subject and recipient"""
        self.message["Subject"] = subject
        self.message["To"] = to_email


    def add_attachment(self, attachment_path: str) -> None:
        """Add an attachment to the email message"""
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(attachment_path)}"',
                )
                self.message.attach(part)

    def send_email(self, to_email: str, body: str) -> None:
        """Send the email message to the specified recipient"""
        body_content = MIMEText(body, "plain")
        self.message.attach(body_content)

        self.server.sendmail(self.from_email, to_email, self.message.as_string())
        print("Email sent successfully.")
    


def send_email(
    subject: str,
    body: str,
    from_email: str,
    password: str,
    to_email: str,
    attachment_path: str = "",
) -> None:
    """Send an email using SMTP"""
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email

    body_content = MIMEText(body, "plain")
    message.attach(body_content)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(attachment_path)}"',
            )
            message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, to_email, message.as_string())
    print("Email sent successfully.")
