from rest_framework_simplejwt.views import TokenRefreshView

from apps.common.api.mixins import PublicAccessMixin


class TokenRefreshAPIView(PublicAccessMixin, TokenRefreshView):
    """
    API endpoint to refresh access token using refresh token.

    Takes a refresh token and returns a new access token.
    """

    pass
