import logging

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)


def _safe_seek(file_obj, offset: int = 0) -> None:

    try:
        file_obj.seek(offset)
    except (OSError, ValueError):
        logger.debug("Unable to seek uploaded file stream.", exc_info=True)


# ---------------
# Validators
# ---------------
# -- TextField validator --
def validate_not_blank(value: str):

    if not value or not value.strip():
        raise ValidationError("A TextField cannot be blank or only a whitespace.")


# -- Image validator --
def validate_image_file(uploaded_file: UploadedFile | None) -> UploadedFile | None:

    if uploaded_file is None:
        return uploaded_file

    max_bytes = 3 * 1024 * 1024  # 3 MB
    if getattr(uploaded_file, "size", 0) > max_bytes:
        raise ValidationError(f"Avatar file is too large (max {max_bytes}MB).")

    allowed_formats = {"JPEG", "PNG", "GIF", "WEBP"}

    # Set to the beginning of the stream
    uploaded_file.seek(0)

    try:
        # 1) Verify as Image
        img = Image.open(uploaded_file)
        img.verify()

        # 2) Re-open for verification
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)

        if not img.format or img.format.upper() not in allowed_formats:
            raise ValidationError(
                f"Unsupported image format. Allowed: {', '.join(sorted(allowed_formats))}."
            )

    except UnidentifiedImageError:
        raise ValidationError("Uploaded file is not a valid image.")
    except (OSError, ValueError):
        raise ValidationError("Image file is corrupted or unreadable.")
    finally:
        _safe_seek(uploaded_file)

    return uploaded_file
