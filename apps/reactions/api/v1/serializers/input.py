from rest_framework import serializers

from apps.reactions.choices import ReactionType


class ReactionInputSerializer(serializers.Serializer):
    reaction_type = serializers.ChoiceField(choices=ReactionType.choices)
