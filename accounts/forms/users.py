import logging

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class UserCreateForm(forms.ModelForm):

    password_confirm = forms.CharField(
        strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "corrent-password"})
    )

    class Meta:
        model = UserModel
        fields = ["username", "first_name", "last_name", "password", "password_confirm"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "username", "focus": True}
            ),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"autocomplete": "corrent-password"}),
        }

    def __init__(self, *args, **kwargs):
        self.email = kwargs.pop("email")

        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if UserModel.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username exists already.")
        return username

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if not username or not password or not password_confirm:
            return cleaned_data

        # 1. Basic Checks
        if not password and not password_confirm:
            raise forms.ValidationError({"password": "Both password fields are requried."})
        if password != password_confirm:
            raise forms.ValidationError({"password": "Passwords do not match."})

        # 2. Validate password
        candidate_user = UserModel(username=username, email=self.email)
        try:
            validate_password(password, user=candidate_user)
        except ValidationError as exc:
            logger.info(
                "%s.validate - Validation of password failed due to policy for "
                "RegistrationToken.email=%s - '%s'.",
                self.__class__.__name__,
                self.email,
                exc.messages,
            )
            raise forms.ValidationError({"password": list(exc.messages)})

        return cleaned_data

    def save(self, email: str, commit=True, **kwargs):

        password = self.cleaned_data["password"]

        obj = super().save(commit=False)
        obj.set_password(password)
        if email:
            obj.email = email
        if commit:
            obj.save()
        return obj
