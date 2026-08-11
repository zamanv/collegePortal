from django.apps import AppConfig
from django.conf import settings


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        # Signals reference the custom user model; only load them when the
        # custom user model is active.
        if settings.AUTH_USER_MODEL == "accounts.User":
            from accounts import signals  # noqa: F401
