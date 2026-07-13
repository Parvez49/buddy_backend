from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

# Formats we're willing to serve back out of media storage. Deliberately not
# every format Pillow can decode (e.g. no BMP/TIFF) — keeps the accepted
# surface small and well-understood.
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}


def sniff_image_format(file: UploadedFile) -> str | None:
    """Return the real, decoded image format (e.g. "JPEG"), or `None` if the
    content doesn't decode as one of `ALLOWED_IMAGE_FORMATS`.

    Reads the file's magic bytes via Pillow rather than trusting the
    client-supplied filename/content_type, which are trivially spoofable.
    Only sniffs — does not enforce size limits, so it's safe to call before
    knowing whether this file will end up classified as an image or video.
    """
    try:
        img_format = Image.open(file).format
    except UnidentifiedImageError, OSError:
        img_format = None
    finally:
        file.seek(0)

    return img_format if img_format in ALLOWED_IMAGE_FORMATS else None


def validate_image_file(image: UploadedFile) -> tuple[int, int]:
    """Reject oversized or corrupt images; return the image's (width, height).

    Callers are expected to have already confirmed via `sniff_image_format`
    that this file decodes as an allowed image format.
    """
    max_size_bytes = settings.MAX_IMAGE_UPLOAD_SIZE_MB * 1024 * 1024
    if image.size > max_size_bytes:
        raise ValidationError(f"Image must be smaller than {settings.MAX_IMAGE_UPLOAD_SIZE_MB}MB.")

    try:
        img = Image.open(image)
        width, height = img.size
        img.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("Upload a valid image file.") from exc
    finally:
        image.seek(0)

    return width, height
