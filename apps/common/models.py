import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampModel(models.Model):
    """
    An abstract model that provides self-updating fields 'created_at' and 'updated_at'
    to track the creation and modification timestamps of a model instance.
    """

    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)

    class Meta:
        abstract = True
        ordering = [
            "-created_at",
        ]

    def get_auto_fields(self):
        return [
            "updated_at",
        ]


class UUIDTimeStampedModel(TimestampModel):
    """Abstract base for all domain models: UUIDv7 primary key + created_at/updated_at.

    UUIDv7 is non-enumerable (no IDOR-by-guessing) while staying time-ordered,
    so B-tree index locality on insert is preserved unlike UUIDv4.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid7,
        editable=False,
    )

    class Meta(TimestampModel.Meta):
        abstract = True
