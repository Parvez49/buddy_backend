from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from apps.notifications.api.v1.serializers import NotificationOutputSerializer
from apps.notifications.models import Notification


@shared_task
def push_notification(notification_id: str) -> None:
    """Push a just-created notification over the recipient's websocket
    group. A no-op, not an error, if the recipient has no active
    connection — `group_send` to an empty group is a normal case.
    """
    try:
        notification = Notification.objects.select_related("actor").get(pk=notification_id)
    except Notification.DoesNotExist:
        return

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user-{notification.recipient_id}-notifications",
        {
            "type": "notification.push",
            "notification": NotificationOutputSerializer(notification).data,
        },
    )
