from rest_framework import serializers


class CommentCreateInputSerializer(serializers.Serializer):
    """Deliberately not a ModelSerializer — `post`, `author`, and `parent`
    are never input fields (mass-assignment guard); they come from the URL
    and `request.user`, resolved by the view and passed to `comment_create`.
    """

    text = serializers.CharField()


class CommentUpdateInputSerializer(serializers.Serializer):
    text = serializers.CharField()
