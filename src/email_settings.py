import smtplib
from email.message import EmailMessage


def get_email(user_email: str, token: str):
    email = EmailMessage()
    email['Subject'] = "Подтверждение регистрации"
    email['From'] = "artemstriver@gmail.com"
    email['To'] = user_email

    email.set_content(
        # TODO исправить текст сообщения + ссылка не работает!!!!
        f"Для подтверждения email, перейдите по ссылке: http://127.0.0.1:8000/auth/verify/{token}",
    )
    return email


def send_email(user_email: str, token: str):
    email = get_email(user_email, token)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("artemstriver@gmail.com", "pttv foby vrfs puiz")
        server.send_message(email)
