from rest_framework import serializers


class LikerOutputSerializer(serializers.Serializer):
    """Read-only representation of one like — works for both `PostLike` and
    `CommentLike` instances, since both have `.user` and `.created_at`.
    """

    id = serializers.UUIDField(source="user.id", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    liked_at = serializers.DateTimeField(source="created_at", read_only=True)
