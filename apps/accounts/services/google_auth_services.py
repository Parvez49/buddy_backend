from django.conf import settings
from django.utils.translation import gettext_lazy as _
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import serializers

_VALID_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


def verify_google_id_token(*, id_token: str) -> dict:
    """Verify a Google-issued ID token and return its claims.

    Checks the signature against Google's live public keys, the issuer, the
    audience (against GOOGLE_OAUTH_CLIENT_IDS), and that Google itself has
    verified the email — that last check is what makes account-linking by
    email safe in user_get_or_create_from_google.

    This makes a network call (to fetch/cache Google's public certs), which
    is why it lives here and not in a serializer's validate_<field>.
    """
    try:
        claims = google_id_token.verify_oauth2_token(
            id_token, google_requests.Request(), audience=None
        )
    except (ValueError, GoogleAuthError) as exc:
        raise serializers.ValidationError(
            _("Invalid or expired Google token.")
        ) from exc

    if claims.get("iss") not in _VALID_ISSUERS:
        raise serializers.ValidationError(_("Invalid Google token issuer."))

    if claims.get("aud") not in settings.GOOGLE_OAUTH_CLIENT_IDS:
        raise serializers.ValidationError(_("Invalid Google token audience."))

    if not claims.get("email_verified"):
        raise serializers.ValidationError(_("Google account email is not verified."))

    return claims
