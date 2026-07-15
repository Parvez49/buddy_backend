from django.db.models import Count, Q, QuerySet

from apps.accounts.models import User
from apps.chat.models import Conversation, Message


def get_conversations(*, user: User) -> QuerySet[Conversation]:
    """`user`'s conversations, most recently active first, each annotated
    with `unread_count` — the number of the *other* participant's messages
    `user` hasn't read yet. A single annotated query for the whole page,
    not one COUNT() per row.
    """
    return (
        Conversation.objects.filter(Q(participant_one=user) | Q(participant_two=user))
        .select_related("participant_one", "participant_two")
        .annotate(
            unread_count=Count(
                "messages", filter=Q(messages__is_read=False) & ~Q(messages__sender=user)
            )
        )
        .order_by("-last_message_at")
    )


def get_conversation_for_user(*, conversation_id: str, user: User) -> Conversation | None:
    """A single conversation, only if `user` is a participant — otherwise
    treated as not found by the caller, not a permission error, same
    "don't confirm existence" rule as a private post.
    """
    return (
        Conversation.objects.filter(Q(participant_one=user) | Q(participant_two=user))
        .filter(pk=conversation_id)
        .select_related("participant_one", "participant_two")
        .first()
    )


def get_messages(*, conversation: Conversation) -> QuerySet[Message]:
    return Message.objects.filter(conversation=conversation).select_related("sender")


def get_other_participant(*, conversation: Conversation, user: User) -> User:
    return (
        conversation.participant_two
        if conversation.participant_one_id == user.pk
        else conversation.participant_one
    )
