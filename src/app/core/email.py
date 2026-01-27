from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="emailkamu@gmail.com",
    MAIL_PASSWORD="APP_PASSWORD_GMAIL",
    MAIL_FROM="emailkamu@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_verify_email(to: str, link: str):
    message = MessageSchema(
        subject="Verifikasi Email",
        recipients=[to],
        body=f"""
Klik link ini untuk verifikasi email kamu:

{link}

Link berlaku 30 menit.
""",
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(message)