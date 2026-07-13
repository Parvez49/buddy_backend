from django.db import models

from apps.accounts.models import User
from apps.comments.models import Comment
from apps.common.models import UUIDTimeStampedModel
from apps.posts.models import Post


class PostLike(UUIDTimeStampedModel):
    """A user's like on a post. Concrete FK, not a GenericForeignKey — see
    ARCHITECTURE.md §16.2: with only two like targets, a generic FK buys
    polymorphism at the cost of real FK integrity and `ON DELETE CASCADE`.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta(UUIDTimeStampedModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="postlike_unique_user_post"),
        ]
        indexes = [
            models.Index(fields=["post", "created_at"], name="postlike_post_created_idx"),
        ]

    def __str__(self) -> str:
        return f"PostLike({self.pk}): user={self.user_id} post={self.post_id}"


class CommentLike(UUIDTimeStampedModel):
    """A user's like on a comment (or reply — same model, see Comment)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_likes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")

    class Meta(UUIDTimeStampedModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"], name="commentlike_unique_user_comment"
            ),
        ]
        indexes = [
            models.Index(fields=["comment", "created_at"], name="commentlike_comment_idx"),
        ]

    def __str__(self) -> str:
        return f"CommentLike({self.pk}): user={self.user_id} comment={self.comment_id}"
