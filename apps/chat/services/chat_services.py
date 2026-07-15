from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User
from apps.chat.models import Conversation, Message
from apps.chat.tasks import push_message

_PREVIEW_LENGTH = 255


def get_or_create_conversation(*, user: User, other: User) -> tuple[Conversation, bool]:
    """Start (or fetch the existing) 1:1 conversation between `user` and
    `other`. No friend-request gating — any two registered users can talk.
    Raises ValidationError for a self-conversation.
    """
    if user.pk == other.pk:
        raise serializers.ValidationError(
            {"participant": ["Cannot start a conversation with yourself."]}
        )

    participant_one, participant_two = sorted([user, other], key=lambda u: u.pk)

    return Conversation.objects.get_or_create(
        participant_one=participant_one,
        participant_two=participant_two,
        defaults={"last_message_at": timezone.now()},
    )


def _clean_text(text: str) -> str:
    """Same whitespace-only guard as comment_services._clean_text."""
    text = text.strip()
    if not text:
        raise serializers.ValidationError({"text": ["This field may not be blank."]})
    return text


@transaction.atomic
def message_send(*, conversation: Conversation, sender: User, text: str) -> Message:
    text = _clean_text(text)
    message = Message.objects.create(conversation=conversation, sender=sender, text=text)

    Conversation.objects.filter(pk=conversation.pk).update(
        last_message_at=message.created_at, last_message_preview=text[:_PREVIEW_LENGTH]
    )

    # After commit — pushing before the row is visible could race a worker
    # reading it, same reasoning as notification_services.notification_create.
    transaction.on_commit(lambda: push_message.delay(str(message.pk)))
    return message


def mark_conversation_read(*, conversation: Conversation, user: User) -> int:
    """Mark every unread message *from the other participant* read. Never
    marks `user`'s own sent messages — a sender can't "read" their own text.
    """
    return (
        Message.objects.filter(conversation=conversation, is_read=False)
        .exclude(sender=user)
        .update(is_read=True)
    )
