from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from apps.accounts.models import User
from apps.comments.constants import MAX_COMMENT_DEPTH
from apps.comments.models import Comment
from apps.notifications.choices import NotificationType
from apps.notifications.services.notification_services import notification_create
from apps.posts.models import Post

_MUTABLE_FIELDS = {"text"}


def _validate_reply_depth(parent: Comment) -> None:
    """A reply's parent must itself be top-level. `parent.parent_id` set
    means `parent` is already at depth 1 — replying to it would be depth 2,
    over the `MAX_COMMENT_DEPTH` cap.
    """
    parent_depth = 0 if parent.parent_id is None else 1
    if parent_depth >= MAX_COMMENT_DEPTH:
        raise serializers.ValidationError({"parent": ["Cannot reply to a reply."]})


def _clean_text(text: str) -> str:
    """Normalize and reject whitespace-only text.

    The DB's `comment_text_required` CHECK only rejects an exact `''` —
    `'   '` satisfies `text <> ''` but has no real content. The API already
    catches this via DRF's CharField (trim_whitespace + allow_blank=False),
    but this is the one place every write path — API today, anything else
    tomorrow — actually goes through, so it's enforced here too rather than
    relying solely on the serializer.
    """
    text = text.strip()
    if not text:
        raise serializers.ValidationError({"text": ["This field may not be blank."]})
    return text


@transaction.atomic
def comment_create(
    *, author: User, post: Post, text: str, parent: Comment | None = None
) -> Comment:
    """Create a comment, or a reply if `parent` is given.

    Raises ValidationError if `parent` is itself a reply (depth cap) or
    belongs to a different post.
    """
    if parent is not None:
        _validate_reply_depth(parent)
        if parent.post_id != post.pk:
            raise serializers.ValidationError(
                {"parent": ["Parent comment does not belong to this post."]}
            )

    comment = Comment.objects.create(
        author=author, post=post, text=_clean_text(text), parent=parent
    )

    if parent is None:
        Post.objects.filter(pk=post.pk).update(comments_count=F("comments_count") + 1)
        notification_create(
            recipient=post.author,
            actor=author,
            notification_type=NotificationType.COMMENT,
            comment=comment,
        )
    else:
        Comment.objects.filter(pk=parent.pk).update(replies_count=F("replies_count") + 1)
        notification_create(
            recipient=parent.author,
            actor=author,
            notification_type=NotificationType.REPLY,
            comment=comment,
        )

    return comment


def comment_update(*, comment: Comment, **fields: str) -> Comment:
    """Update mutable fields on an existing comment or reply."""
    unknown_fields = set(fields) - _MUTABLE_FIELDS
    if unknown_fields:
        raise ValueError(f"Cannot update fields: {sorted(unknown_fields)}")

    if "text" in fields:
        fields["text"] = _clean_text(fields["text"])

    for field, value in fields.items():
        setattr(comment, field, value)
    comment.save(update_fields=[*fields.keys(), "updated_at"])
    return comment


@transaction.atomic
def comment_delete(*, comment: Comment) -> None:
    """Delete a comment or reply. Deleting a top-level comment cascades to
    its replies (and all their likes) via `ON DELETE CASCADE`.
    """
    if comment.parent_id is not None:
        Comment.objects.filter(pk=comment.parent_id).update(replies_count=F("replies_count") - 1)
    else:
        Post.objects.filter(pk=comment.post_id).update(comments_count=F("comments_count") - 1)

    comment.delete()
