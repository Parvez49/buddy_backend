from rest_framework import serializers

from apps.posts.models import Post, PostMedia


class PostAuthorOutputSerializer(serializers.Serializer):
    """Compact author representation embedded in a post — deliberately not
    the full `UserOutputSerializer`: a feed reader shouldn't get every
    viewer's email address for free.
    """

    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(read_only=True)


class PostMediaOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = (
            "id",
            "file",
            "media_type",
            "order",
            "width",
            "height",
            "duration_seconds",
            "mime_type",
            "file_size",
        )
        read_only_fields = fields


class PostOutputSerializer(serializers.ModelSerializer):
    """Read-only representation of a Post — used by the feed, retrieve,
    create, and update responses.
    """

    author = PostAuthorOutputSerializer(read_only=True)
    media = PostMediaOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "text",
            "media",
            "visibility",
            "likes_count",
            "comments_count",
            "edited_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
