from django.db import transaction

from apps.accounts.models import User
from apps.comments.models import Comment
from apps.notifications.models import Notification
from apps.notifications.tasks import push_notification
from apps.posts.models import Post


def notification_create(
    *,
    recipient: User,
    actor: User,
    notification_type: str,
    post: Post | None = None,
    comment: Comment | None = None,
) -> Notification | None:
    """Create a notification for `recipient`, triggered by `actor`. No-op
    if `actor` is `recipient` (e.g. commenting on your own post) — nobody
    needs to be notified about their own activity.

    Dispatches the real-time push only after the enclosing transaction
    commits (`transaction.on_commit`) — this is always called from inside
    an already-`@transaction.atomic` caller (comment_create, post_react,
    comment_react), so pushing before commit could race a worker reading a
    row that isn't visible yet.
    """
    if recipient.pk == actor.pk:
        return None

    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        post=post,
        comment=comment,
    )
    transaction.on_commit(lambda: push_notification.delay(str(notification.pk)))
    return notification


def mark_notification_read(*, notification: Notification) -> None:
    """Idempotent — marking an already-read notification is a no-op."""
    if notification.is_read:
        return
    notification.is_read = True
    notification.save(update_fields=["is_read", "updated_at"])


def mark_all_notifications_read(*, user: User) -> int:
    """Returns the number of notifications actually flipped to read."""
    return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
