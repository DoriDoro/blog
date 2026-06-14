from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models.functions import Lower

from accounts.models import Profile, Website
from utils.admin.actions import make_user_active, make_user_inactive, make_active, make_inactive

UserModel = get_user_model()


@admin.register(UserModel)
class CustomUserAdmin(UserAdmin):

    model = UserModel
    list_display = ["username", "email", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["username", "email"]
    date_hierarchy = "date_joined"
    show_facets = admin.ShowFacets.ALWAYS
    list_per_page = 20
    ordering = [Lower("username")]
    actions = [make_user_active, make_user_inactive]
    fieldsets = (
        (
            None,
            {"fields": ("username", "email", "password")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["username", "can_be_contacted", "can_data_be_shared"]
    list_filter = ["can_be_contacted", "can_data_be_shared"]
    search_fields = ["username"]
    date_hierarchy = "created"
    show_facets = admin.ShowFacets.ALWAYS
    list_per_page = 20
    ordering = [Lower("username")]
    actions = [make_active, make_inactive]

    @admin.display(description="Username")
    def username(self, obj):
        return obj.user.username


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "username"]
    search_fields = ["name", "username"]
    date_hierarchy = "created"
    show_facets = admin.ShowFacets.ALWAYS
    list_per_page = 20
    ordering = [Lower("name")]
    actions = [make_active, make_inactive]

    @admin.display(description="Username")
    def username(self, obj):
        return obj.profile.user.username
