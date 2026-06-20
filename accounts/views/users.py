import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import CreateView

from accounts.forms import UserCreateForm
from accounts.models import RegistrationToken
from accounts.models.register_token import DEFAULT_EXPIRATION_DAYS
from utils.emailing import on_commit_send_verify_email

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class UserCreateView(CreateView):

    model = UserModel
    form_class = UserCreateForm
    template_name = "users/create.html"
    success_url = reverse_lazy("accounts:login")

    @cached_property
    def registration_token(self):
        token = self.kwargs["token"]
        return get_object_or_404(RegistrationToken, token=token)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["email"] = self.registration_token.email
        return kwargs

    @transaction.atomic
    def form_valid(self, form):

        if not self.registration_token.email_verified:
            if self.registration_token.is_expired:
                messages.warning(
                    self.request, "Your link has expired. Please start registration again."
                )
                return HttpResponseRedirect(
                    reverse("accounts:registration:registration_start_process")
                )

            build_email_verify_path = reverse(
                "accounts:registration:registration_verify_email",
                kwargs={"token": self.registration_token.token},
            )
            built_email_verify_url = self.request.build_absolute_uri(build_email_verify_path)
            logger.info(
                "%s.form_valid - Built email_verify_url=%s.",
                self.__class__.__name__,
                built_email_verify_url,
            )
            on_commit_send_verify_email(
                expire_days=DEFAULT_EXPIRATION_DAYS,
                email_verify_url=built_email_verify_url,
                to_email=self.registration_token.email,
            )
            logger.info(
                "%s.form_valid - Email not yet verified, verify_email send.",
                self.__class__.__name__,
            )
            messages.success(self.request, "An email was sent to verify your email address.")
            return HttpResponseRedirect(self.success_url)

        if not self.registration_token.is_used:
            self.object = form.save(email=self.registration_token.email)
            self.registration_token.mark_user_created_at()
            logger.info(
                "%s.form_valid - New User created: email=%s, username=%s",
                self.__class__.__name__,
                self.object.email,
                self.object.username,
            )
            messages.success(self.request, "Your account is already active. Please log in.")
            return HttpResponseRedirect(self.success_url)

        messages.error(self.request, "There was an error, please contact the page's support.")
        return HttpResponseRedirect(self.success_url)
