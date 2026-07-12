import os
from collections.abc import Callable

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from apps.accounts.models import User
from apps.accounts.selectors.user_selectors import get_user_by_email
from apps.accounts.services.user_services import user_create, user_create_superuser

# Only ever used as a fallback, and only when DEBUG=True (see _resolve_password).
# Not a real credential — nosec: bandit B105 (hardcoded_password_string).
_DEV_FALLBACK_PASSWORD = "dev-only-changeme"  # nosec B105

DEFAULT_ACCOUNTS = (
    {
        "label": "superuser",
        "create_fn": user_create_superuser,
        "email": "email@email.com",
        "first_name": "super",
        "last_name": "user",
        "password_env": "DEFAULT_SUPERUSER_PASSWORD",
    },
    {
        "label": "general user",
        "create_fn": user_create,
        "email": "user@email.com",
        "first_name": "general",
        "last_name": "user",
        "password_env": "DEFAULT_USER_PASSWORD",
    },
)


class Command(BaseCommand):
    help = (
        "Create the default superuser and general user for local development. "
        "Idempotent — safe to run repeatedly, existing accounts are left untouched."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="If an account already exists, reset its password instead of skipping it.",
        )

    def handle(self, *args, **options) -> None:
        for account in DEFAULT_ACCOUNTS:
            self._seed_account(reset_password=options["reset_password"], **account)

    def _seed_account(
        self,
        *,
        reset_password: bool,
        label: str,
        create_fn: Callable[..., User],
        email: str,
        first_name: str,
        last_name: str,
        password_env: str,
    ) -> None:
        existing = get_user_by_email(email=email)
        if existing is not None and not reset_password:
            self.stdout.write(
                self.style.WARNING(f"Skipped {label} — {email} already exists.")
            )
            return

        password = self._resolve_password(label=label, password_env=password_env)

        if existing is not None:
            existing.set_password(password)
            existing.save(update_fields=["password"])
            self.stdout.write(
                self.style.SUCCESS(f"Reset password for {label} — {email}")
            )
            return

        create_fn(
            email=email, password=password, first_name=first_name, last_name=last_name
        )
        self.stdout.write(self.style.SUCCESS(f"Created {label} — {email}"))

    def _resolve_password(self, *, label: str, password_env: str) -> str:
        password = os.environ.get(password_env)
        if password:
            return password

        if not settings.DEBUG:
            raise CommandError(
                f"{password_env} is not set. Refusing to create the default {label} "
                f"with a fallback password outside DEBUG — set {password_env} explicitly."
            )
        return _DEV_FALLBACK_PASSWORD
