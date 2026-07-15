from rest_framework import serializers

from apps.comments.models import Comment


class CommentAuthorOutputSerializer(serializers.Serializer):
    """Compact author representation — same reasoning as posts: a reader
    shouldn't get every commenter's email address for free.
    """

    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True)


class CommentOutputSerializer(serializers.ModelSerializer):
    """Read-only representation of a Comment — used for both top-level
    comments and replies; they're the same resource shape.
    """

    author = CommentAuthorOutputSerializer(read_only=True)
    # A Subquery() annotation from the comment selectors, not a model field —
    # "like"/"dislike"/None, default=None covers instances that didn't go
    # through one of those selectors (e.g. the object
    # comment_create()/comment_update() just made).
    my_reaction = serializers.CharField(read_only=True, default=None, allow_null=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "post",
            "parent",
            "author",
            "text",
            "likes_count",
            "dislikes_count",
            "replies_count",
            "my_reaction",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
