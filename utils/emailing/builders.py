from utils.emailing.models import EmailPayload
from utils.emailing.settings import required_settings
from utils.emailing.texts import TEXT_VERIFY_EMAIL


def build_verify_email(*, expire_days: int, email_verify_url: str) -> EmailPayload:

    cfg = required_settings("PLATFORM_NAME", "SUPPORT_EMAIL")

    return EmailPayload(
        subject="Verify your email address",
        template_name="email/verify_email.html",
        context={
            "verify_url": email_verify_url,
            "expire_days": expire_days,
            "support_email": cfg["SUPPORT_EMAIL"],
            "platform_name": cfg["PLATFORM_NAME"],
        },
        text_body=TEXT_VERIFY_EMAIL.format(
            verify_url=email_verify_url,
            expire_days=expire_days,
            support_email=cfg["SUPPORT_EMAIL"],
            platform_name=cfg["PLATFORM_NAME"],
        ),
    )
