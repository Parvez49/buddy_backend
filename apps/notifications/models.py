from django.db import models

from apps.accounts.models import User
from apps.comments.models import Comment
from apps.common.models import UUIDTimeStampedModel
from apps.notifications.choices import NotificationType
from apps.posts.models import Post


class Notification(UUIDTimeStampedModel):
    """One notification for `recipient`, triggered by `actor` doing
    something to `post` or `comment` — exactly one of the two is set,
    depending on `notification_type` (`notification_create_exactly_one_target`).

    No `title`/`message` field: the human-readable text is built in the
    output serializer from `notification_type` + `actor`, so it can't go
    stale if the actor later changes their name — same reasoning as not
    denormalizing anything else derivable from an FK.
    """

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    is_read = models.BooleanField(default=False)

    class Meta(UUIDTimeStampedModel.Meta):
        indexes = [
            # This recipient's notifications, newest first — matches
            # FeedCursorPagination's (-created_at, -id) ordering exactly.
            models.Index(
                fields=["recipient", "-created_at", "-id"], name="notification_recipient_idx"
            ),
            # Partial: unread-count reads hit this constantly, read
            # notifications never do.
            models.Index(
                fields=["recipient"],
                name="notification_unread_idx",
                condition=models.Q(is_read=False),
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(post__isnull=False, comment__isnull=True)
                    | models.Q(post__isnull=True, comment__isnull=False)
                ),
                name="notification_exactly_one_target",
            ),
        ]

    def __str__(self) -> str:
        return f"Notification({self.pk}) to {self.recipient_id}: {self.notification_type}"
