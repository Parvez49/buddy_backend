import uuid

from django.db.models import QuerySet

from apps.accounts.models import User


def get_user_by_email(*, email: str) -> User | None:
    """Return the user with the given email (case-insensitive), or None."""
    return User.objects.filter(email=email.lower()).first()


def get_user_by_id(*, user_id: uuid.UUID | str) -> User | None:
    """Return the user with the given id, or None."""
    return User.objects.filter(pk=user_id).first()


def get_users_excluding(*, user: User) -> QuerySet[User]:
    """All active users except `user` — backs the "Your Friends" / people
    list. There's no friends/follow concept yet, so this is everyone.
    """
    return User.objects.filter(is_active=True).exclude(pk=user.pk).order_by("first_name", "last_name")
