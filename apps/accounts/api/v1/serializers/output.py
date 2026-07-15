from rest_framework import serializers

from apps.accounts.models import User


class UserOutputSerializer(serializers.ModelSerializer):
    """Read-only representation of a User — used by register, login, and /auth/me/."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "full_name", "email", "avatar", "created_at")
        read_only_fields = fields


class TokenPairOutputSerializer(serializers.Serializer):
    """Read-only shape of a JWT access/refresh token pair."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
