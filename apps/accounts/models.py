from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import UserManager
from apps.common.models import UUIDTimeStampedModel


class User(UUIDTimeStampedModel, AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(verbose_name=_("First Name"), max_length=150)
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=150)
    email = models.EmailField(verbose_name=_("Email Address"), unique=True, db_index=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # No upload endpoint yet — settable via /admin/ in the meantime. Output
    # serializers expose it as a nullable relative URL, same pattern as
    # apps.posts.PostMedia (see apps/accounts/api/v1/serializers/output.py).
    avatar = models.ImageField(
        verbose_name=_("Avatar"), upload_to="accounts/avatars/", null=True, blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta(UUIDTimeStampedModel.Meta):
        db_table = "accounts_user"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
