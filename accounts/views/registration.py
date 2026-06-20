import logging
import uuid

from django.db import transaction
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import FormView
from django.urls import reverse

from accounts.forms import UserRegistrationRequestForm
from accounts.models import RegistrationToken
from accounts.models.register_token import DEFAULT_EXPIRATION_DAYS
from utils.emailing import on_commit_send_verify_email

logger = logging.getLogger(__name__)


class UserRegisterRequestView(FormView):

    form_class = UserRegistrationRequestForm
    template_name = "registration/email_request.html"

    @transaction.atomic
    def form_valid(self, form):

        email = form.cleaned_data["email"]

        reg_token, created = RegistrationToken.rotate_or_create(email=email)
        self.token = reg_token.token

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
            messages.success(self.request, "An email was sent to verify your email address.")
            return HttpResponseRedirect(reverse("accounts:login"))

        messages.success(self.request, "Please create your account.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("accounts:user:user_create", kwargs={"token": self.token})


class UserVerifyEmailView(View):

    http_method_names = ["get"]

    @transaction.atomic
    def get(self, request, token: uuid.UUID):

        reg_token = get_object_or_404(RegistrationToken.objects.select_for_update(), token=token)

        if reg_token.is_used:
            logger.info(
                "%s.get - RegistrationToken is already used, email=%s has a User.",
                self.__class__.__name__,
                reg_token.email,
            )
            messages.info(request, "Your account is already active. Please log in.")
            return HttpResponseRedirect(reverse("accounts:login"))

        if reg_token.is_expired:
            logger.info(
                "%s.get - RegistrationToken expired, email=%s.",
                self.__class__.__name__,
                reg_token.email,
            )
            messages.warning(
                request, "Your verification link has expired. Please request a new one."
            )
            return HttpResponseRedirect(
                reverse("accounts:registration:registration_start_process")
            )
        if reg_token.email_verified:
            messages.info(request, "Your email is already verified. Please create your account.")
            return HttpResponseRedirect(
                reverse("accounts:user:user_create", kwargs={"token": reg_token.token})
            )

        reg_token.mark_email_verified()
        messages.success(request, "Your email address was verified.")
        return HttpResponseRedirect(
            reverse("accounts:user:user_create", kwargs={"token": reg_token.token})
        )
