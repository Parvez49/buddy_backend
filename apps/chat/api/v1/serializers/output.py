from rest_framework import serializers

from apps.chat.models import Conversation, Message


class ChatParticipantOutputSerializer(serializers.Serializer):
    """Same compact shape as `apps.posts...PostAuthorOutputSerializer`."""

    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True)


class MessageOutputSerializer(serializers.ModelSerializer):
    sender = ChatParticipantOutputSerializer(read_only=True)
    conversation_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Message
        fields = ("id", "conversation_id", "sender", "text", "is_read", "created_at")
        read_only_fields = fields


class ConversationOutputSerializer(serializers.ModelSerializer):
    """`other_participant` is resolved relative to the caller — the view
    must pass `context={"request": request}` when instantiating this
    directly (DRF's `get_serializer()` does this automatically for the
    list endpoint; the POST /conversations/ view does it explicitly).
    """

    other_participant = serializers.SerializerMethodField()
    unread_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Conversation
        fields = (
            "id",
            "other_participant",
            "last_message_preview",
            "last_message_at",
            "unread_count",
            "created_at",
        )
        read_only_fields = fields

    def get_other_participant(self, obj: Conversation):
        request_user = self.context["request"].user
        other = (
            obj.participant_two
            if obj.participant_one_id == request_user.pk
            else obj.participant_one
        )
        return ChatParticipantOutputSerializer(other).data
