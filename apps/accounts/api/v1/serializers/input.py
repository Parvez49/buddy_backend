from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.selectors.user_selectors import get_user_by_email
from apps.common.api.fields import PasswordField


class RegisterInputSerializer(serializers.Serializer):
    """Validates registration input.

    Deliberately not a ModelSerializer — it never touches the ORM for
    creation. The view passes `validated_data` straight to the `user_create`
    service. Email uniqueness is still checked here (a ModelSerializer would
    give this for free via UniqueValidator) so a duplicate registration
    fails with a clean 400 instead of an unhandled IntegrityError.
    """

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = PasswordField()

    def validate_email(self, value: str) -> str:
        if get_user_by_email(email=value) is not None:
            raise serializers.ValidationError(
                _("A user with this email already exists.")
            )
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class LoginInputSerializer(serializers.Serializer):
    """Authenticates email + password and exposes the resolved user via validated_data['user']."""

    email = serializers.EmailField(label=_("Email"))
    password = PasswordField()

    def validate(self, attrs: dict) -> dict:
        user = authenticate(
            request=self.context.get("request"),
            email=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError(
                _("Invalid email or password."), code="authorization"
            )
        if not user.is_active:
            raise serializers.ValidationError(
                _("This account has been disabled."), code="authorization"
            )
        attrs["user"] = user
        return attrs


class LogoutInputSerializer(serializers.Serializer):
    """Validates and blacklists a refresh token."""

    refresh = serializers.CharField(label=_("Refresh token"))

    def validate_refresh(self, value: str) -> str:
        try:
            RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError(_("Invalid or expired refresh token."))
        return value

    def save(self, **kwargs) -> None:
        RefreshToken(self.validated_data["refresh"]).blacklist()
