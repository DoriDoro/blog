from dataclasses import dataclass


@dataclass(frozen=True)
class EmailSendResult:

    sent: bool
    used_html: bool
    num_sent: int
    template_found: bool


@dataclass(frozen=True)
class EmailPayload:
    subject: str
    template_name: str | None
    context: dict
    text_body: str
    from_email: str | None = None
    reply_to: str | None = None


class EmailSendError(Exception):
    pass
