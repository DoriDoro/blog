from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.db import models


# --- UserModel Managers ---
class ActiveUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username: str, email: str, password: str, **extra_fields: dict):
        if not username:
            raise ValueError("The 'username' is required.")
        if not email:
            raise ValueError("The 'email' is required.")
        email = self.normalize_email(email).lower()
        user = self.model(username=username.strip(), email=email, **extra_fields)
        if password:
            validate_password(password=password, user=user)
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, username: str, email: str, password: str = None, **extra_fields: dict):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username: str, email: str, password: str, **extra_fields: dict):
        if not password:
            raise ValueError("A superuser must have a password.")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have 'is_staff=True'.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have 'is_superuser=True'.")

        return self._create_user(username, email, password, **extra_fields)


# --- Profile Managers ---
class CanBeContactedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(can_be_contacted=True)


class CanDataBeSharedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(can_data_be_shared=True)
