from rest_framework import serializers


class ReactorOutputSerializer(serializers.Serializer):
    """Read-only representation of one reaction — works for both
    `PostReaction` and `CommentReaction` instances, since both have `.user`,
    `.reaction_type`, and `.created_at`.
    """

    id = serializers.UUIDField(source="user.id", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    avatar = serializers.ImageField(source="user.avatar", read_only=True)
    reaction_type = serializers.CharField(read_only=True)
    reacted_at = serializers.DateTimeField(source="created_at", read_only=True)
