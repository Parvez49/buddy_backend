from django.db import models

from apps.accounts.models import User
from apps.comments.models import Comment
from apps.common.models import UUIDTimeStampedModel
from apps.posts.models import Post
from apps.reactions.choices import ReactionType


class PostReaction(UUIDTimeStampedModel):
    """A user's reaction (like/dislike) to a post — one row per (user, post),
    `reaction_type` holds which one.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_reactions")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    reaction_type = models.CharField(max_length=10, choices=ReactionType.choices)

    class Meta(UUIDTimeStampedModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="postreaction_unique_user_post"),
        ]
        indexes = [
            models.Index(fields=["post", "created_at"], name="postreaction_post_created_idx"),
        ]

    def __str__(self) -> str:
        return (
            f"PostReaction({self.pk}): user={self.user_id} "
            f"post={self.post_id} type={self.reaction_type}"
        )


class CommentReaction(UUIDTimeStampedModel):
    """A user's reaction (like/dislike) to a comment (or reply — same model,
    see Comment). Same shape/rationale as `PostReaction`.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_reactions")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions")
    reaction_type = models.CharField(max_length=10, choices=ReactionType.choices)

    class Meta(UUIDTimeStampedModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"], name="commentreaction_unique_user_comment"
            ),
        ]
        indexes = [
            models.Index(fields=["comment", "created_at"], name="commentreaction_comment_idx"),
        ]

    def __str__(self) -> str:
        return (
            f"CommentReaction({self.pk}): user={self.user_id} "
            f"comment={self.comment_id} type={self.reaction_type}"
        )
