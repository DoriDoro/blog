from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower

from accounts.models.managers import UserManager, ActiveUserManager


class CustomUser(AbstractUser):

    email = models.EmailField(
        unique=True,
        db_index=True,
        error_messages={"unique": "User with this email address exists already."},
        verbose_name="email address",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()
    active_users = ActiveUserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="uq_user_lower_email",
                violation_error_code="unique_email",
                violation_error_message="User with this email address exists already.",
            )
        ]

    def __str__(self):
        return f"{self.email} - {self.username}"

    def _normalize_fields(self):
        if self.email:
            self.email = self.email.strip().lower()

    def save(self, *args, **kwargs):
        self._normalize_fields()
        self.full_clean()
        super().save(*args, **kwargs)
