from django.db import models

from apps.accounts.models import User
from apps.common.models import UUIDTimeStampedModel


class Conversation(UUIDTimeStampedModel):
    """A 1:1 conversation between two users — no group chat, no
    friend-request gating (any registered user can start one with any
    other).

    `participant_one`/`participant_two` are normalized so
    `participant_one_id < participant_two_id` (enforced in
    chat_services.get_or_create_conversation) — that's what makes
    `UniqueConstraint(participant_one, participant_two)` catch "this
    conversation already exists" regardless of who started it, same
    reasoning as apps.reactions' one-row-per-(user, target) constraint.
    """

    participant_one = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    participant_two = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")

    # Denormalized — avoids a join to Message for every row on the
    # conversation list, same reasoning as Post.likes_count (ARCHITECTURE.md
    # §16.3). Set at creation (to created_at) and on every new message —
    # never null, so "-last_message_at" ordering never needs a NULLS
    # position decision.
    last_message_at = models.DateTimeField()
    last_message_preview = models.CharField(max_length=255, blank=True, default="")

    class Meta(UUIDTimeStampedModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["participant_one", "participant_two"],
                name="conversation_unique_participants",
            ),
            models.CheckConstraint(
                condition=models.Q(participant_one__lt=models.F("participant_two")),
                name="conversation_participants_ordered",
            ),
        ]
        indexes = [
            models.Index(
                fields=["participant_one", "-last_message_at"],
                name="conversation_p1_idx",
            ),
            models.Index(
                fields=["participant_two", "-last_message_at"],
                name="conversation_p2_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"Conversation({self.pk}): {self.participant_one_id} <-> {self.participant_two_id}"


class Message(UUIDTimeStampedModel):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    text = models.TextField()
    # Thread-level granularity, not per-message like Notification — opening
    # a conversation marks the whole thing read, matching real chat UX.
    is_read = models.BooleanField(default=False)

    class Meta(UUIDTimeStampedModel.Meta):
        indexes = [
            models.Index(
                fields=["conversation", "-created_at", "-id"], name="message_conversation_idx"
            ),
        ]
        constraints = [
            models.CheckConstraint(condition=~models.Q(text=""), name="message_text_required"),
        ]

    def __str__(self) -> str:
        return f"Message({self.pk}) in Conversation({self.conversation_id})"
