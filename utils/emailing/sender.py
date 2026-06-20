import logging
import smtplib
import socket

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from typing import Optional

from utils.emailing.models import EmailSendResult, EmailPayload, EmailSendError

logger = logging.getLogger(__name__)


def send_email(
    *,
    subject: str,
    to: list[str],
    text_body: str,
    from_email: Optional[str] = None,
    reply_to: Optional[str] = None,
    template_name: Optional[str] = None,
    context: Optional[dict] = None,
) -> EmailSendResult:

    from_email = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None)

    if not subject:
        raise ValueError("A 'subject' must be set.")
    if not to:
        raise ValueError("'to' must contain at least one recipient.")
    if not from_email:
        raise ValueError("'DEFAULT_FROM_EMAIL' is not configured.")
    if not text_body:
        raise ValueError("A plain-text fallback as 'text_body' is required.")

    html_body = None
    template_found = False
    if template_name:
        try:
            html_body = render_to_string(template_name, context or {})
            template_found = True
        except TemplateDoesNotExist:
            logger.warning(
                "send_email - Email template '%s' not found, falling back to plain text.",
                template_name,
            )
        except Exception:
            logger.exception("send_email - Failed to find template '%s'.", template_name)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=to,
        reply_to=[reply_to] if reply_to else None,
    )

    if html_body:
        message.attach_alternative(html_body, "text/html")

    try:
        num_sent = message.send()
    except smtplib.SMTPException as exc:
        logger.error("SMTP error sending to %s: %s", to, exc)
        raise EmailSendError(str(exc)) from exc
    except (socket.timeout, socket.gaierror) as exc:
        logger.error("Network error sending to %s: %s", to, exc)
        raise EmailSendError(str(exc)) from exc

    if num_sent == 0:
        logger.error(
            "send_email - '%s' to %s: SMTP accepted the connection but reported 0 delivered.",
            subject,
            to,
        )
    else:
        logger.info("send_email - '%s' sent to %s (html=%s)", subject, to, bool(html_body))

    return EmailSendResult(
        sent=num_sent > 0,
        used_html=bool(html_body),
        num_sent=num_sent,
        template_found=template_found,
    )


def send_payload(*, payload: EmailPayload, to_email: str) -> EmailSendResult:

    result = send_email(
        subject=payload.subject,
        to=[to_email],
        template_name=payload.template_name,
        context=payload.context,
        text_body=payload.text_body,
        from_email=payload.from_email,
        reply_to=payload.reply_to,
    )

    if not result.sent:
        logger.error(
            "send_payload - 0 messages delivered to '%s' (subject: '%s').",
            to_email,
            payload.subject,
        )
    return result
