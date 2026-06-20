from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from typing import Any


def required_settings(*names: str) -> dict[str, Any]:

    missing = [name for name in names if not getattr(settings, name, None)]
    if missing:
        raise ImproperlyConfigured(f"Missing required settings: {', '.join(missing)}")
    return {name: getattr(settings, name) for name in names}
