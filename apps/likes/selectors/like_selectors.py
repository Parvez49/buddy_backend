from django.db.models import QuerySet

from apps.comments.models import Comment
from apps.likes.models import CommentLike, PostLike
from apps.posts.models import Post


def get_post_likers(*, post: Post) -> QuerySet[PostLike]:
    """Users who liked `post`, most recent like first."""
    return PostLike.objects.filter(post=post).select_related("user").order_by("-created_at")


def get_comment_likers(*, comment: Comment) -> QuerySet[CommentLike]:
    """Users who liked `comment` (or reply), most recent like first."""
    return (
        CommentLike.objects.filter(comment=comment).select_related("user").order_by("-created_at")
    )
