from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User


def generate_jwt_token_for_user(user: User) -> dict[str, str]:
    """Generate a JWT token pair for the given user."""
    token = RefreshToken.for_user(user)
    return {
        "refresh": str(token),
        "access": str(token.access_token),
    }
