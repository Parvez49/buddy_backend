from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from apps.posts.choices import MediaType
from apps.posts.validators.image_validators import sniff_image_format, validate_image_file
from apps.posts.validators.video_validators import sniff_video_container, validate_video_file


@dataclass(frozen=True)
class ValidatedMedia:
    file: UploadedFile
    media_type: str
    mime_type: str
    file_size: int
    width: int | None = None
    height: int | None = None
    duration_seconds: int | None = None


def validate_and_classify_media(file: UploadedFile) -> ValidatedMedia:
    """Detect the real media type from content — never the client-supplied
    filename/content_type — then run the type-specific validator (size
    limit, corruption check).
    """
    image_format = sniff_image_format(file)
    if image_format is not None:
        width, height = validate_image_file(file)
        return ValidatedMedia(
            file=file,
            media_type=MediaType.IMAGE,
            mime_type=f"image/{image_format.lower()}",
            file_size=file.size,
            width=width,
            height=height,
        )

    video_mime_type = sniff_video_container(file)
    if video_mime_type is not None:
        validate_video_file(file)
        return ValidatedMedia(
            file=file,
            media_type=MediaType.VIDEO,
            mime_type=video_mime_type,
            file_size=file.size,
        )

    raise ValidationError(
        "Unsupported media type — upload an image (JPEG/PNG/WEBP/GIF) or a video (MP4/WEBM)."
    )
