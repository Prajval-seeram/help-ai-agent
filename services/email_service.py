import smtplib

from email.mime.text import MIMEText

from config.settings import (
    SMTP_EMAIL,
    SMTP_PASSWORD
)


def send_email(
        to_email,
        subject,
        body
):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(
        "smtp.gmail.com",
        587
    ) as server:

        server.starttls()

        server.login(
            SMTP_EMAIL,
            SMTP_PASSWORD
        )

        server.send_message(
            msg
        )