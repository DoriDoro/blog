from django.urls import include, path

from accounts import views

app_name = "accounts"


# accounts/registration/...
# accounts:registration
registration_patterns = [
    path(
        "start-process/",
        views.UserRegisterRequestView.as_view(),
        name="registration_start_process",
    ),
    path(
        "email-verification/<uuid:token>/",
        views.UserRegisterRequestView.as_view(),
        name="registration_verify_email",
    ),
]

# accounts/user/...
# accounts:user
user_patterns = [
    path("create/", views.UserRegisterRequestView.as_view(), name="user_create"),
]

# accounts/...
urlpatterns = [
    path("login/", views.UserRegisterRequestView.as_view(), name="login"),
    path("registration/", include((registration_patterns, "registration"))),
    path("user/", include((user_patterns, "user"))),
]
