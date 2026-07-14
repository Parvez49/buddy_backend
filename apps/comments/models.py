from django.db import models

from apps.accounts.models import User
from apps.common.models import UUIDTimeStampedModel
from apps.posts.models import Post


class Comment(UUIDTimeStampedModel):
    """A comment on a post, or a reply to a comment if `parent` is set.

    There is no separate `Reply` model — a reply is structurally identical
    to a comment. Depth is capped at 1 (no reply-to-a-reply), enforced in
    comment_services.comment_create(), not here.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    text = models.TextField()

    # Denormalized — maintained via F() inside the same transaction as the
    # underlying reaction/reply insert. Never read via COUNT(*). A user
    # holds at most one reaction (like/dislike, see apps.reactions), so
    # these two never both move for the same event.
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)

    class Meta(UUIDTimeStampedModel.Meta):
        indexes = [
            # Top-level comments on a post, newest first. Partial: replies
            # (parent IS NOT NULL) never hit this query path.
            models.Index(
                fields=["post", "-created_at", "-id"],
                name="comment_post_top_level_idx",
                condition=models.Q(parent__isnull=True),
            ),
            # Replies to a given comment, oldest first (thread reading order).
            models.Index(fields=["parent", "created_at", "id"], name="comment_replies_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=~models.Q(text=""), name="comment_text_required"),
        ]

    def __str__(self) -> str:
        return f"Comment({self.pk}) by {self.author_id} on Post({self.post_id})"
