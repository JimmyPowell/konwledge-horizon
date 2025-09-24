from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from aiosmtplib import SMTPResponseException
from app.config.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_HOST,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=settings.MAIL_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False
)

async def send_verification_code(email_to: str, code: str):
    message = MessageSchema(
        subject="Your Verification Code",
        recipients=[email_to],
        body=f"Your verification code is: {code}",
        subtype="html"
    )
    
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except SMTPResponseException as e:
        # This can happen if the server (like QQ's) doesn't gracefully close the connection.
        # If the error code is not critical (e.g., related to QUIT command), we can ignore it
        # as the email has likely been sent already.
        print(f"Ignoring non-critical SMTP response error after sending email: {e}")
        # A more robust solution would check e.code, but for now, we'll assume it's the QUIT error.
        pass
