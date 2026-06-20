import logging

from django.db import transaction
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from django.urls import reverse

from accounts.forms import UserRegistrationRequestForm
from accounts.models import RegistrationToken
from accounts.models.register_token import DEFAULT_EXPIRATION_DAYS
from utils.emailing import on_commit_send_verify_email

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class UserRegisterRequestView(FormView):

    model = RegistrationToken
    form_class = UserRegistrationRequestForm
    template_name = "registration/email_request.html"

    @transaction.atomic
    def form_valid(self, form):

        email = form.cleaned_data["email"]

        reg_token, created = RegistrationToken.rotate_or_create(email=email)

        build_email_verify_path = reverse(
            "accounts:registration:registration_verify_email", kwargs={"token": reg_token.token}
        )
        built_email_verify_url = self.request.build_absolute_uri(build_email_verify_path)
        logger.info(
            "%s.form_valid - Built email_verify_url=%s.",
            self.__class__.__name__,
            built_email_verify_url,
        )

        if created:
            on_commit_send_verify_email(
                expire_days=DEFAULT_EXPIRATION_DAYS,
                email_verify_url=built_email_verify_url,
                to_email=email,
            )
            logger.info("%s.form_valid - Email verify_email send.", self.__class__.__name__)
            messages.success(self.request, "An email was send to verify your email address.")
            return HttpResponseRedirect(reverse("accounts:login"))

        if not reg_token.email_verified:
            on_commit_send_verify_email(
                expire_days=DEFAULT_EXPIRATION_DAYS,
                email_verify_url=built_email_verify_url,
                to_email=email,
            )
            logger.info(
                "%s.form_valid - Email not yet verified, verify_email send.",
                self.__class__.__name__,
            )
            messages.success(self.request, "An email was send to verify your email address.")
            return HttpResponseRedirect(reverse("accounts:login"))

        if reg_token.email_verified and not reg_token.is_expired:
            messages.success(self.request, "Please create your account.")
            return HttpResponseRedirect(reverse("accounts:user:user_create"))

        messages.error(self.request, "There was an error, please contact the page's support.")
        return HttpResponseRedirect(reverse("accounts:login"))
