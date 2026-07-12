from rest_framework.permissions import AllowAny


class PublicAccessMixin:
    """Mixin to allow public access to API views."""

    authentication_classes = []
    permission_classes = [AllowAny]
