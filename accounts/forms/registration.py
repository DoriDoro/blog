import logging

from django import forms
from django.contrib.auth import get_user_model

from accounts.models import RegistrationToken

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class UserRegistrationRequestForm(forms.Form):

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "autofocus": True, "autocomplete": "email"}
        ),
        help_text="Enter a valid email address.",
    )

    default_error_messages = {
        "account_exists": "The registration process is already done.",
    }

    def clean_email(self):
        value = (self.cleaned_data["email"] or "").strip().lower()
        return value

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data["email"]

        token_qs = RegistrationToken.objects.filter(
            email__iexact=email, user_created_at__isnull=True
        )
        user_qs = UserModel.objects.filter(email__iexact=email)

        if token_qs.exists():
            logger.info(
                "%S.clean - Attempt to register with known email=%s.",
                self.__class__.__name__,
                email,
            )
        if user_qs.exists():
            logger.info(
                "%s.clean - Registration attempt for already exissting UserModel.email=%s.",
                self.__class__.__name__,
                email,
            )
            raise forms.ValidationError([self.default_error_messages["account_exists"]])

        return cleaned_data
