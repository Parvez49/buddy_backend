from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from apps.chat.api.v1.serializers import MessageOutputSerializer
from apps.chat.models import Message


@shared_task
def push_message(message_id: str) -> None:
    """Push a just-sent message to both participants' personal chat groups.
    No per-conversation group — with exactly two participants, pushing
    straight to each one's `user-{id}-chat` group (same shape as
    `apps.notifications.tasks.push_notification`) needs no dynamic
    subscription bookkeeping for brand-new conversations. A no-op, not an
    error, if a participant has no active connection.
    """
    try:
        message = Message.objects.select_related("sender", "conversation").get(pk=message_id)
    except Message.DoesNotExist:
        return

    conversation = message.conversation
    payload = {"type": "message.new", "message": MessageOutputSerializer(message).data}

    channel_layer = get_channel_layer()
    for participant_id in (conversation.participant_one_id, conversation.participant_two_id):
        async_to_sync(channel_layer.group_send)(f"user-{participant_id}-chat", payload)
