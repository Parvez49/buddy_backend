from collections.abc import Callable

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from apps.accounts.models import User
from apps.accounts.selectors.user_selectors import get_user_by_email


def _create_user(
    *,
    manager_method: Callable[..., User],
    email: str,
    password: str | None,
    first_name: str,
    last_name: str,
) -> User:
    """Shared create path for user_create/user_create_superuser.

    The serializer already checks email uniqueness, but that check and this
    insert aren't atomic — two concurrent registrations for the same email
    can both pass validation. Catch the resulting IntegrityError here so the
    loser gets a clean, DRF-recognized error instead of an unhandled 500.
    """
    try:
        return manager_method(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
    except IntegrityError as exc:
        raise serializers.ValidationError(
            {"email": [ErrorDetail("A user with this email already exists.", code="unique")]}
        ) from exc


def user_create(*, email: str, password: str, first_name: str, last_name: str) -> User:
    """Create a new regular user account with a hashed password."""
    return _create_user(
        manager_method=User.objects.create_user,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


def user_create_superuser(*, email: str, password: str, first_name: str, last_name: str) -> User:
    """Create a superuser account with a hashed password."""
    return _create_user(
        manager_method=User.objects.create_superuser,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


def user_get_or_create_from_google(
    *, email: str, first_name: str, last_name: str
) -> tuple[User, bool]:
    """Get the user for a Google-verified email, or create one on first sign-in.

    The email is already confirmed by Google before this is called (see
    google_auth_services.verify_google_id_token), so linking by email is
    safe even if the account was originally created with a password —
    Google's own verification is the trust anchor, not ours.
    """
    user = get_user_by_email(email=email)
    if user is not None:
        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["This account has been disabled."]}
            )
        return user, False

    user = _create_user(
        manager_method=User.objects.create_user,
        email=email,
        password=None,  # set_password(None) -> set_unusable_password(): Google-only account
        first_name=first_name,
        last_name=last_name,
    )
    return user, True


def user_update(*, user: User, **fields: str) -> User:
    """Update mutable profile fields on an existing user."""
    allowed_fields = {"first_name", "last_name"}
    unknown_fields = set(fields) - allowed_fields
    if unknown_fields:
        raise ValueError(f"Cannot update fields: {sorted(unknown_fields)}")

    for field, value in fields.items():
        setattr(user, field, value)
    user.save(update_fields=[*fields.keys(), "updated_at"])
    return user
