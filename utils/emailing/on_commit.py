import logging

from django.db import transaction

from utils.emailing.models import EmailSendError
from utils.emailing.builders import build_verify_email, build_first_login_email
from utils.emailing.sender import send_payload

logger = logging.getLogger(__name__)


def on_commit_send_verify_email(*, expire_days: int, email_verify_url: str, to_email: str):

    payload = build_verify_email(expire_days=expire_days, email_verify_url=email_verify_url)

    def _send():
        try:
            send_payload(payload=payload, to_email=to_email)
        except EmailSendError:
            logger.error(
                "on_commit_send_verify_email - Failed to send verify email to %s.", to_email
            )
        except Exception:
            logger.exception(
                "on_commit_send_verify_email - Unexpected error sending to %s.", to_email
            )

    transaction.on_commit(_send)


def on_commit_send_first_login_email(*, login_url: str, to_email: str):
    payload = build_first_login_email(login_url=login_url)

    def _send():
        try:
            send_payload(payload=payload, to_email=to_email)
        except EmailSendError:
            logger.error(
                "on_commit_send_verify_email - Failed to send verify email to %s.", to_email
            )
        except Exception:
            logger.exception(
                "on_commit_send_verify_email - Unexpected error sending to %s.", to_email
            )

    transaction.on_commit(_send)
