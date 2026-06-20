import uuid
import logging

from datetime import timedelta
from django.db import IntegrityError, transaction, models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)

DEFAULT_EXPIRATION_DAYS = 7


def default_expires_at():
    return timezone.now() + timedelta(days=DEFAULT_EXPIRATION_DAYS)


class RegistrationToken(models.Model):

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(db_index=True)

    verified_at = models.DateTimeField(blank=True, null=True, db_index=True)
    expires_at = models.DateTimeField(default=default_expires_at, db_index=True)
    user_created_at = models.DateTimeField(blank=True, null=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                condition=Q(user_created_at__isnull=True),
                name="uq_token_no_user_email",
                violation_error_code="unique_email",
                violation_error_message="RegistrationToken with that email exists already.",
            ),
            models.CheckConstraint(
                condition=Q(expires_at__gt=F("created")),
                name="ck_token_expires_after_created",
                violation_error_code="check_expires_after_creation",
                violation_error_message="'expires_at' must be set after 'created'.",
            ),
        ]
        indexes = [
            models.Index(
                fields=["token", "email", "expires_at"],
                name="idx_token_email_expires",
            ),
            models.Index(fields=["verified_at", "expires_at"], name="idx_token_verified_expires"),
        ]
        ordering = ["-created", "-pk"]

    def __str__(self):
        return f"RegToken: {self.email}"

    def _normalize_fields(self):
        if self.email:
            self.email = self.email.strip().lower()

    def clean(self):
        super().clean()
        errors: dict[str, str] = {}

        if self.expires_at:
            if self.verified_at is None and self.expires_at <= timezone.now():
                errors["expires_at"] = "'expires_at' must be set in future."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        clean = kwargs.pop("clean", True)
        self._normalize_fields()
        if clean:
            self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_used(self) -> bool:
        return self.user_created_at is not None

    @property
    def is_expired(self) -> bool:
        """Only meaningful while awaiting email verification."""
        return self.verified_at is None and timezone.now() >= self.expires_at

    @property
    def email_verified(self) -> bool:
        return self.verified_at is not None

    @property
    def is_pending(self) -> bool:
        now = timezone.now()
        return self.verified_at is None and now < self.expires_at

    @classmethod
    def rotate_or_create(cls, *, email: str) -> tuple["RegistrationToken", bool]:

        email = (email or "").strip().lower()
        set_expires_at = timezone.now() + timedelta(days=DEFAULT_EXPIRATION_DAYS)

        try:
            reg_token = cls.objects.create(email=email)
            logger.info(
                "%s.rotate_or_create - New RegistrationToken created for email=%s.",
                cls.__class__.__name__,
                email,
            )
            return reg_token, True
        except (ValidationError, IntegrityError):
            try:
                with transaction.atomic():
                    rotate_token = cls.objects.select_for_update().get(
                        email__iexact=email, user_created_at__isnull=True
                    )
                    if rotate_token.is_expired:
                        rotate_token.expires_at = set_expires_at
                        rotate_token.token = uuid.uuid4()
                        rotate_token.save(update_fields=["expires_at", "token", "updated"])
                        logger.info(
                            "%s.rotate_or_create - Expired RegistrationToken updated for email=%s.",
                            cls.__class__,
                            email,
                        )
                        return rotate_token, False
                    logger.info(
                        "%s.rotate_or_create - RegistrationToken retrieved for email=%s.",
                        cls.__class__,
                        email,
                    )
                    return rotate_token, False
            except cls.DoesNotExist:
                logger.exception(
                    "%s.rotate_or_create - Creation or rotation failed for email=%s.",
                    cls.__class__,
                    email,
                )
                raise

    def mark_email_verified(self, *, commit: bool = True):

        now = timezone.now()

        errors: dict[str, str] = {}

        if self.email_verified:
            errors["verified_at"] = "Email already verified."
        if self.is_used:
            errors["user_created_at"] = "UserModel already created."
        if self.is_expired:
            errors["expires_at"] = "Imposible to verify when RegistrationToken is expired."

        if errors:
            raise ValidationError(errors)

        self.verified_at = now
        if commit:
            self.save(update_fields=["verified_at", "updated"])
            logger.info(
                "%s.mark_email_verified - RegistrationToken.verified_at modified.",
                self.__class__.__name__,
            )

    def mark_user_created_at(self, *, commit: bool = True):

        now = timezone.now()

        errors: dict[str, str] = {}
        if self.is_used:
            errors["user_created_at"] = "UserModel already created for this RegistrationToken."
        if not self.email_verified:
            errors["verified_at"] = (
                "RegistrationToken.verified_at must be set before creating a User."
            )
        if errors:
            raise ValidationError(errors)

        self.user_created_at = now
        if commit:
            self.save(update_fields=["user_created_at", "updated"], clean=False)
            logger.info(
                "%s.mark_email_verified - RegistrationToken.user_created_at modified.",
                self.__class__.__name__,
            )
