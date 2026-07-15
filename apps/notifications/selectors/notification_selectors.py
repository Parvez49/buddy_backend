from django.db.models import QuerySet

from apps.accounts.models import User
from apps.notifications.models import Notification


def get_notifications(*, user: User) -> QuerySet[Notification]:
    """`user`'s notifications, newest first."""
    return Notification.objects.filter(recipient=user).select_related("actor")


def get_notification_for_user(*, notification_id: str, user: User) -> Notification | None:
    """A single notification, only if `user` is its recipient — a
    notification belonging to someone else is treated as not found by the
    caller, not a permission error.
    """
    return (
        Notification.objects.filter(pk=notification_id, recipient=user)
        .select_related("actor")
        .first()
    )


def get_unread_count(*, user: User) -> int:
    return Notification.objects.filter(recipient=user, is_read=False).count()
