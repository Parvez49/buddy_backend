from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

# Magic-byte signatures for the containers we accept. No Pillow equivalent
# exists for video, so this checks the container header directly instead of
# decoding — good enough to reject non-video uploads, not a full codec
# validation. Width/height/duration extraction needs a real decode pass
# (ffprobe or similar) and is deferred — see PostMedia.width/height/duration.
_MP4_QT_BRAND_OFFSET = 4
_MP4_QT_BRAND = b"ftyp"
_WEBM_MAGIC = b"\x1a\x45\xdf\xa3"


def sniff_video_container(file: UploadedFile) -> str | None:
    """Return a mime type ("video/mp4" / "video/webm") if the file's header
    matches a known video container, else `None`.
    """
    header = file.read(12)
    file.seek(0)

    brand = header[_MP4_QT_BRAND_OFFSET : _MP4_QT_BRAND_OFFSET + 4]
    if len(header) >= 8 and brand == _MP4_QT_BRAND:
        return "video/mp4"
    if header[:4] == _WEBM_MAGIC:
        return "video/webm"
    return None


def validate_video_file(video: UploadedFile) -> None:
    """Reject oversized videos.

    Callers are expected to have already confirmed via `sniff_video_container`
    that this file's header matches an allowed container.
    """
    max_size_bytes = settings.MAX_VIDEO_UPLOAD_SIZE_MB * 1024 * 1024
    if video.size > max_size_bytes:
        raise ValidationError(f"Video must be smaller than {settings.MAX_VIDEO_UPLOAD_SIZE_MB}MB.")
