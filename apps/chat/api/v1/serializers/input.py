from rest_framework import serializers


class ConversationStartInputSerializer(serializers.Serializer):
    participant = serializers.UUIDField()


class MessageCreateInputSerializer(serializers.Serializer):
    text = serializers.CharField(trim_whitespace=True, allow_blank=False)
