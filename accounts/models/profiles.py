from django.conf import settings
from django.db import models
from django.db.models.functions import Lower

from accounts.models.managers import CanBeContactedManager, CanDataBeSharedManager
from utils.database import upload_to, private_storage, validate_not_blank, validate_image_file


class Profile(models.Model):

    bio = models.TextField(validators=[validate_not_blank])

    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)

    avatar = models.ImageField(
        upload_to=upload_to,
        storage=private_storage,
        validators=[validate_image_file],
        blank=True,
        null=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )

    objects = models.Manager()
    can_contact_profiles = CanBeContactedManager()
    can_share_data_profiles = CanDataBeSharedManager()

    def __str__(self):
        return f"Profile: {self.user}"

    @property
    def joined(self):
        return f"Joined on {self.created.strftime('%B %d, %Y')}"


class Website(models.Model):

    name = models.CharField(max_length=150, db_index=True)
    url = models.URLField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    profile = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="websites"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("url"),
                "profile",
                name="uq_website_low_url_profile",
                violation_error_code="unique_url",
                violation_error_message="This Website exists already for this Profile.",
            )
        ]
        ordering = [Lower("name"), "pk"]
