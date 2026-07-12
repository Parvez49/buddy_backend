from typing import TYPE_CHECKING

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from apps.accounts.models import User


class UserManager(BaseUserManager):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        if not email:
            raise ValueError(_("Users must have an email address"))
        # normalize_email() only lowercases the domain part; citext isn't in
        # play until Postgres is provisioned (Phase 2), so lowercase fully
        # here to keep email uniqueness case-insensitive in the meantime.
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)
