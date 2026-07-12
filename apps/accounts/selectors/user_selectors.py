import uuid

from apps.accounts.models import User


def get_user_by_email(*, email: str) -> User | None:
    """Return the user with the given email (case-insensitive), or None."""
    return User.objects.filter(email=email.lower()).first()


def get_user_by_id(*, user_id: uuid.UUID | str) -> User | None:
    """Return the user with the given id, or None."""
    return User.objects.filter(pk=user_id).first()
