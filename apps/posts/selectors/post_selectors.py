import uuid

from django.db.models import OuterRef, Q, QuerySet, Subquery

from apps.accounts.models import User
from apps.posts.choices import PostVisibility
from apps.posts.models import Post
from apps.reactions.models import PostReaction


def get_feed_posts(*, user: User) -> QuerySet[Post]:
    """Posts visible to `user`: all PUBLIC posts plus their own PRIVATE ones.

    `my_reaction` is a `Subquery()` annotation, not a per-row query — one
    indexed subquery for the whole page, not one query per post.
    """
    return (
        Post.objects.filter(Q(visibility=PostVisibility.PUBLIC) | Q(author=user))
        .select_related("author")
        .prefetch_related("media")
        .annotate(
            my_reaction=Subquery(
                PostReaction.objects.filter(user=user, post=OuterRef("pk")).values("reaction_type")[
                    :1
                ]
            )
        )
        .order_by("-created_at", "-id")
    )


def get_post_for_user(*, post_id: uuid.UUID | str, user: User) -> Post | None:
    """Return `post_id` if visible to `user`, else `None`.

    "Visible" means PUBLIC, or PRIVATE and owned by `user`. Callers must
    turn `None` into a 404, never a 403 — a private post's existence must
    never leak to anyone but its owner.
    """
    return (
        Post.objects.filter(pk=post_id)
        .filter(Q(visibility=PostVisibility.PUBLIC) | Q(author=user))
        .select_related("author")
        .prefetch_related("media")
        .annotate(
            my_reaction=Subquery(
                PostReaction.objects.filter(user=user, post=OuterRef("pk")).values("reaction_type")[
                    :1
                ]
            )
        )
        .first()
    )
