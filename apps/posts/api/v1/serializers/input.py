from rest_framework import serializers

from apps.posts.choices import PostVisibility
from apps.posts.constants import MAX_MEDIA_PER_POST
from apps.posts.validators import validate_and_classify_media


def _validate_media_list(files: list) -> list:
    if len(files) > MAX_MEDIA_PER_POST:
        raise serializers.ValidationError(
            f"A post can have at most {MAX_MEDIA_PER_POST} media items."
        )
    return [validate_and_classify_media(file) for file in files]


class PostCreateInputSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True, default="")
    media = serializers.ListField(
        child=serializers.FileField(), required=False, default=list, allow_empty=True
    )
    visibility = serializers.ChoiceField(
        choices=PostVisibility.choices, default=PostVisibility.PUBLIC
    )

    def validate_media(self, files):
        return _validate_media_list(files)


class PostUpdateInputSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True)
    media = serializers.ListField(child=serializers.FileField(), required=False, allow_empty=True)
    visibility = serializers.ChoiceField(choices=PostVisibility.choices, required=False)

    def validate_media(self, files):
        return _validate_media_list(files)
