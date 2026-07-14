from django.db.models import QuerySet

from apps.comments.models import Comment
from apps.posts.models import Post
from apps.reactions.models import CommentReaction, PostReaction


def get_post_reactors(*, post: Post) -> QuerySet[PostReaction]:
    """Reactions on `post`, most recent first. Filtering to a single
    `reaction_type` (e.g. "who liked this") is applied by `ReactionFilter`
    at the view layer via `?reaction_type=`, not here.
    """
    return PostReaction.objects.filter(post=post).select_related("user").order_by("-created_at")


def get_comment_reactors(*, comment: Comment) -> QuerySet[CommentReaction]:
    """Reactions on `comment` (or reply). See `get_post_reactors`."""
    return (
        CommentReaction.objects.filter(comment=comment)
        .select_related("user")
        .order_by("-created_at")
    )
