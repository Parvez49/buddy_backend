from django.db import transaction
from django.db.models import F

from apps.accounts.models import User
from apps.comments.models import Comment
from apps.likes.models import CommentLike, PostLike
from apps.posts.models import Post


@transaction.atomic
def post_like(*, user: User, post: Post) -> tuple[PostLike, bool]:
    """Like `post` as `user`. Idempotent: re-liking is a no-op, not an error.

    `get_or_create` (not check-then-insert) resolves the race between two
    concurrent likes via the `UNIQUE(user, post)` constraint instead of
    fighting it — see ARCHITECTURE.md §8.
    """
    like, created = PostLike.objects.get_or_create(user=user, post=post)
    if created:
        Post.objects.filter(pk=post.pk).update(likes_count=F("likes_count") + 1)
    return like, created


@transaction.atomic
def post_unlike(*, user: User, post: Post) -> bool:
    """Unlike `post` as `user`. Idempotent: unliking something never liked is
    a no-op, not an error — two concurrent unlikes race-freely resolve to
    "at most one row deleted," since a DELETE that matches nothing just
    affects zero rows rather than erroring.
    """
    deleted, _ = PostLike.objects.filter(user=user, post=post).delete()
    if deleted:
        Post.objects.filter(pk=post.pk).update(likes_count=F("likes_count") - 1)
    return bool(deleted)


@transaction.atomic
def comment_like(*, user: User, comment: Comment) -> tuple[CommentLike, bool]:
    """Like `comment` (or reply) as `user`. Idempotent — see `post_like`."""
    like, created = CommentLike.objects.get_or_create(user=user, comment=comment)
    if created:
        Comment.objects.filter(pk=comment.pk).update(likes_count=F("likes_count") + 1)
    return like, created


@transaction.atomic
def comment_unlike(*, user: User, comment: Comment) -> bool:
    """Unlike `comment` (or reply) as `user`. Idempotent — see `post_unlike`."""
    deleted, _ = CommentLike.objects.filter(user=user, comment=comment).delete()
    if deleted:
        Comment.objects.filter(pk=comment.pk).update(likes_count=F("likes_count") - 1)
    return bool(deleted)
