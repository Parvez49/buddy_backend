from rest_framework import serializers

from apps.notifications.choices import NotificationType
from apps.notifications.models import Notification

_MESSAGE_TEMPLATES: dict[str, str] = {
    NotificationType.COMMENT: "{actor} commented on your post",
    NotificationType.REPLY: "{actor} replied to your comment",
    NotificationType.POST_REACTION: "{actor} reacted to your post",
    NotificationType.COMMENT_REACTION: "{actor} reacted to your comment",
}


class NotificationActorOutputSerializer(serializers.Serializer):
    """Compact actor representation — same shape as
    `apps.posts.api.v1.serializers.output.PostAuthorOutputSerializer`.
    """

    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True)


class NotificationOutputSerializer(serializers.ModelSerializer):
    actor = NotificationActorOutputSerializer(read_only=True)
    # `post_id`/`comment_id` read straight off the FK column — no join
    # needed, exactly one is non-null (`notification_exactly_one_target`).
    post_id = serializers.UUIDField(read_only=True, allow_null=True)
    comment_id = serializers.UUIDField(read_only=True, allow_null=True)
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "actor",
            "notification_type",
            "post_id",
            "comment_id",
            "message",
            "is_read",
            "created_at",
        )
        read_only_fields = fields

    def get_message(self, obj: Notification) -> str:
        template = _MESSAGE_TEMPLATES.get(obj.notification_type, "")
        return template.format(actor=obj.actor.full_name)
