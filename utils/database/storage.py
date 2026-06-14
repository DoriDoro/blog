import uuid
import os

from django.core.files.storage import storages
from django.db.models import Model


def upload_to(instance: Model, filename: str) -> str:

    ext = os.path.splitext(filename)[1].lower()
    model_name = instance.__class__.__name__.lower()
    new_filename = uuid.uuid4().hex
    return f"uploads/{model_name}/{new_filename}{ext}"


def private_storage():

    try:
        return storages["private"]
    except KeyError as exc:
        raise KeyError(
            "Privat storage backend not configured. Set 'private' in settings.STORAGES."
        ) from exc
