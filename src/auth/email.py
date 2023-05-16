from typing import List

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from jinja2 import Environment, select_autoescape, PackageLoader

from src.config import EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM, EMAIL_PORT, EMAIL_HOST

env = Environment(
    loader=PackageLoader('src', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class Email:
    def __init__(self, username: str, url: str, email: List[EmailStr]):
        self.username = username
        self.sender = 'Codevo <admin@admin.com>'
        self.email = email
        self.url = url
        pass

    async def send_mail(self, subject, template):

        conf = ConnectionConfig(
            MAIL_USERNAME=EMAIL_USERNAME,
            MAIL_PASSWORD=EMAIL_PASSWORD,
            MAIL_FROM=EMAIL_FROM,
            MAIL_PORT=EMAIL_PORT,
            MAIL_SERVER=EMAIL_HOST,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

        template = env.get_template(template)

        html = template.render(
            url=self.url,
            username=self.username,
            subject=subject
        )

        # Define the message options
        message = MessageSchema(
            subject=subject,
            recipients=self.email,
            body=html,
            subtype="html"
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)

    async def send_verification_code(self):
        await self.send_mail('Your verification code (Valid for 10min)', 'auth/verification.html')
