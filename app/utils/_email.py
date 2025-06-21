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

    BODY_NO_BALANCE = "No balance left in account. Available balance - {}. All schedules have been deleted."
    BODY_NO_MATCHES_FOUND = "No suitable matches found for the next day."
    BODY_NOT_LOGGED_IN = "Bot was unable to log in."
    BODY_MATCHES_SCHEDULED = "Scheduled {} match(es) for next day."
    BODY_PLACED_BET = "Placed bet on match {}."
    BODY_CHANGED_ODD = "Odds have changed for match {} - {}. Bet not placed. Initial odd: {}, actual odd: {}."
    BODY_UNCAUGHT_EXCEPTION = (
        "An uncaught exception occurred. See attached log file for details."
    )

    def __init__(self, from_email: str, password: str) -> None:
        self.from_email = from_email
        self.password = password

        self.server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        self.server.login(from_email, password)

        self.message = MIMEMultipart("alternative")

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

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        events: list[dict] = [],
        traceback_logs_path: str = None,
        image_path: str = None,
    ) -> None:
        """Send the email message to the specified recipient"""

        self.message["Subject"] = subject
        self.message["From"] = self.from_email
        self.message["To"] = to_email

        if traceback_logs_path:
            self.add_attachment(traceback_logs_path)

        if image_path:
            self.add_attachment(image_path)

        body = "<h3>{}</h3>".format(body)
        if events:
            body += "<br><h4>Summary</h4><br>"
            table = "<table border>{}</table>"
            table_content = ""

            table_headers = events[0].keys()
            table_headers = [
                header.replace("_", " ").title() for header in table_headers
            ]
            table_header_row = "<tr>{}</tr>".format(
                "".join(f"<th>{header}</th>" for header in table_headers)
            )
            table_content += table_header_row

            for event in events:
                row = "<tr>{}</tr>".format(
                    "".join(f"<td>{e}</td>" for e in event.values())
                )
                table_content += row

            body += table.format(table_content)

        body_content = MIMEText(body, "html")
        self.message.attach(body_content)

        self.server.sendmail(self.from_email, to_email, self.message.as_string())
        print("Email sent successfully.")
        self.close()

    def close(self) -> None:
        """Close the SMTP server connection"""
        try:
            self.server.quit()
        except Exception as e:
            print(f"Error while closing SMTP connection: {e}")
