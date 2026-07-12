from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.accounts.api.v1.serializers import LoginInputSerializer
from apps.accounts.utils import generate_jwt_token_for_user
from apps.common.api.mixins import PublicAccessMixin
from apps.common.throttling import LoginRateThrottle


class LoginAPIView(PublicAccessMixin, GenericAPIView):
    """Authenticate with email + password and return a JWT token pair."""

    serializer_class = LoginInputSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        return Response(generate_jwt_token_for_user(user))
