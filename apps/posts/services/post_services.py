from collections.abc import Sequence

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User
from apps.posts.choices import PostVisibility
from apps.posts.models import Post, PostMedia
from apps.posts.validators import ValidatedMedia

_MUTABLE_FIELDS = {"text", "media", "visibility"}


def _validate_has_content(*, text: str, media_count: int) -> None:
    """Mirrors the retired `post_text_or_image_required` DB CheckConstraint,
    which can no longer be a single-table CHECK now that media lives in a
    related table. Enforced here instead, so a bad request fails with a
    clean 400 rather than an empty, content-less post being created.
    """
    if not text and media_count == 0:
        raise serializers.ValidationError(
            {"non_field_errors": ["A post must have text or at least one media item."]}
        )


def _create_media(*, post: Post, media: Sequence[ValidatedMedia]) -> None:
    # One .save() per item (not bulk_create): FileField only writes its
    # content to storage during Model.save(), which bulk_create skips.
    for order, item in enumerate(media):
        PostMedia.objects.create(
            post=post,
            file=item.file,
            media_type=item.media_type,
            order=order,
            width=item.width,
            height=item.height,
            duration_seconds=item.duration_seconds,
            file_size=item.file_size,
            mime_type=item.mime_type,
        )


@transaction.atomic
def post_create(
    *,
    author: User,
    text: str = "",
    media: Sequence[ValidatedMedia] = (),
    visibility: str = PostVisibility.PUBLIC,
) -> Post:
    """Create a new post with its attached media, atomically."""
    _validate_has_content(text=text, media_count=len(media))
    post = Post.objects.create(author=author, text=text, visibility=visibility)
    _create_media(post=post, media=media)
    return post


@transaction.atomic
def post_update(*, post: Post, **fields) -> Post:
    """Update mutable fields on an existing post. Only keys present in
    `fields` are touched — callers pass a partial-update's `validated_data`
    straight through. Passing `media` replaces the post's entire media set.
    """
    unknown_fields = set(fields) - _MUTABLE_FIELDS
    if unknown_fields:
        raise ValueError(f"Cannot update fields: {sorted(unknown_fields)}")

    media = fields.pop("media", None)
    for field, value in fields.items():
        setattr(post, field, value)

    media_count = len(media) if media is not None else post.media.count()
    _validate_has_content(text=post.text, media_count=media_count)

    post.edited_at = timezone.now()
    post.save(update_fields=[*fields.keys(), "edited_at", "updated_at"])

    if media is not None:
        post.media.all().delete()
        _create_media(post=post, media=media)

    return post


def post_delete(*, post: Post) -> None:
    """Delete a post (cascades to its media rows)."""
    post.delete()
