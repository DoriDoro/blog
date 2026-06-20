from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        from utils.emailing.settings import required_settings

        required_settings("PLATFORM_NAME", "SUPPORT_EMAIL", "DEFAULT_FROM_EMAIL")
