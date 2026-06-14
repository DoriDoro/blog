import logging

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def _log_admin_action(*, request, queryset, field_name: str, value: bool, updated: int):
    """Record the outcome of a shared admin bulk-update action."""

    logger.info(
        "admin action executed: actor_email=%s model=%s field=%s value=%s " "updated=%s.",
        getattr(request.user, "email", None),
        queryset.model._meta.label,
        field_name,
        value,
        updated,
    )


@admin.action(description=_("Mark User as 'active'"))
def make_user_active(modeladmin, request, queryset):
    """Mark the selected user records as active."""

    updated = queryset.update(is_active=True)
    _log_admin_action(
        request=request,
        queryset=queryset,
        field_name="is_active",
        value=True,
        updated=updated,
    )
    modeladmin.message_user(request, _("%d item(s) marked as 'active'.") % updated)


@admin.action(description=_("Mark User as 'inactive'"))
def make_user_inactive(modeladmin, request, queryset):
    """Mark the selected user records as inactive."""

    updated = queryset.update(is_active=False)
    _log_admin_action(
        request=request,
        queryset=queryset,
        field_name="is_active",
        value=False,
        updated=updated,
    )
    modeladmin.message_user(request, _("%d item(s) marked as 'inactive'.") % updated)


@admin.action(description=_("Mark selected as 'active'"))
def make_active(modeladmin, request, queryset):
    """Mark the selected model records as active."""

    updated = queryset.update(active=True)
    _log_admin_action(
        request=request,
        queryset=queryset,
        field_name="active",
        value=True,
        updated=updated,
    )
    modeladmin.message_user(request, _("%d item(s) marked as 'active'.") % updated)


@admin.action(description=_("Mark selected as 'inactive'"))
def make_inactive(modeladmin, request, queryset):
    """Mark the selected model records as inactive."""

    updated = queryset.update(active=False)
    _log_admin_action(
        request=request,
        queryset=queryset,
        field_name="active",
        value=False,
        updated=updated,
    )
    modeladmin.message_user(request, _("%d item(s) marked as 'inactive'.") % updated)
