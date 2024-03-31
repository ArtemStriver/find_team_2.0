import smtplib
from email.message import EmailMessage

from src.config import settings


def get_email(
    user_email: str,
    subject: str,
    content_with_token: str,
) -> EmailMessage:
    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = settings.EMAIL_HOST_USER
    email["To"] = user_email

    email.set_content(content_with_token)
    return email


def send_email(user_email: str, subject: str, content_with_token: str):
    email = get_email(user_email, subject, content_with_token)
    with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(email)
