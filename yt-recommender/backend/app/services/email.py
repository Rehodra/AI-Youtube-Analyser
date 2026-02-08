from pprint import pprint
import smtplib
from email.message import EmailMessage
from pydantic import EmailStr
from app.core.config import settings

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

SENDER_EMAIL = settings.email
APP_PASSWORD = str(settings.password)


def send_email(
    to_email: EmailStr,
    subject: str,
    body: str,
    is_html: bool = False,
):
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    if is_html:
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
            pprint(f"Email sent to {to_email}")
            
    except Exception as e:        # log this properly in real apps
        raise RuntimeError(f"Email sending failed: {e}")
    
    except smtplib.SMTPException as e:
        # log this properly in real apps
        raise RuntimeError(f"Email sending failed: {e}")
