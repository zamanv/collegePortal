"""Reusable image upload validators.

Used on profile image fields and enforced again by the profile edit views so
that uploads are rejected before they reach storage.
"""

import os

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
}

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

DEFAULT_MAX_IMAGE_SIZE_MB = 5


@deconstructible
class ImageTypeValidator:
    """Reject uploads that are not supported image types."""

    def __call__(self, value):
        content_type = getattr(value, "content_type", None)
        if content_type and content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise ValidationError(
                f"Unsupported file type '{content_type}'. Please upload a JPEG, "
                "PNG, GIF, WebP or BMP image."
            )

        extension = os.path.splitext(value.name)[1].lower()
        if extension and extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(
                f"Unsupported file extension '{extension}'. Please upload a JPEG, "
                "PNG, GIF, WebP or BMP image."
            )


@deconstructible
class MaxImageSizeValidator:
    """Reject images larger than ``max_mb`` megabytes."""

    def __init__(self, max_mb=DEFAULT_MAX_IMAGE_SIZE_MB):
        self.max_mb = max_mb

    def __call__(self, value):
        size = getattr(value, "size", None)
        if size is not None and size > self.max_mb * 1024 * 1024:
            raise ValidationError(
                f"Image is too large ({filesizeformat(size)}). Maximum allowed "
                f"size is {self.max_mb} MB."
            )
