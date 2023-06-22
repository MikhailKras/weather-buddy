import smtplib
from email.message import EmailMessage
from typing import List
from pydantic import EmailStr
from jinja2 import Environment, select_autoescape, PackageLoader

from src.config import EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM, EMAIL_PORT, EMAIL_HOST

env = Environment(
    loader=PackageLoader('src', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class Email:
    def __init__(self, username: str, url: str, email: List[EmailStr]):
        self.username = username
        self.sender = '<weather_buddy@example.com>'
        self.email = email
        self.url = url

    def send_mail(self, subject, template):
        template = env.get_template(template)

        html = template.render(
            url=self.url,
            username=self.username,
            subject=subject
        )

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = ', '.join(self.email)
        msg.set_content(html, subtype='html')

        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)

    def send_verification_code(self):
        self.send_mail('Email Verification for WeatherBuddy (valid for 10 minutes)', 'auth/verification_message.html')

    def send_reset_password_mail(self):
        self.send_mail('Reset Password email for WeatherBuddy (valid for 10 minutes)', 'auth/reset_password/email_message.html')
