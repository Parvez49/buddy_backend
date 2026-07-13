import uuid

from django.db.models import Q, QuerySet

from apps.accounts.models import User
from apps.comments.models import Comment
from apps.posts.choices import PostVisibility
from apps.posts.models import Post


def get_post_comments(*, post: Post) -> QuerySet[Comment]:
    """Top-level comments on `post`, newest first. Replies are excluded —
    they're fetched per-comment via `get_comment_replies`.
    """
    return (
        Comment.objects.filter(post=post, parent__isnull=True)
        .select_related("author")
        .order_by("-created_at", "-id")
    )


def get_comment_replies(*, comment: Comment) -> QuerySet[Comment]:
    """Replies to `comment`, oldest first — matches thread reading order."""
    return (
        Comment.objects.filter(parent=comment).select_related("author").order_by("created_at", "id")
    )


def get_comment_for_user(*, comment_id: uuid.UUID | str, user: User) -> Comment | None:
    """Return `comment_id` if its post is visible to `user`, else `None`.

    Mirrors posts' 404-not-403 rule: a comment on a private post the
    requester doesn't own must be indistinguishable from one that doesn't
    exist — otherwise comments would leak the private post's existence.
    """
    return (
        Comment.objects.filter(pk=comment_id)
        .filter(Q(post__visibility=PostVisibility.PUBLIC) | Q(post__author=user))
        .select_related("author", "post")
        .first()
    )
