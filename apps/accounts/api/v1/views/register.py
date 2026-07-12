from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.accounts.api.v1.serializers import (
    RegisterInputSerializer,
    UserOutputSerializer,
)
from apps.accounts.services.user_services import user_create
from apps.accounts.utils import generate_jwt_token_for_user
from apps.common.api.mixins import PublicAccessMixin
from apps.common.throttling import RegistrationRateThrottle


class RegisterAPIView(PublicAccessMixin, GenericAPIView):
    """Register a new user and return the created profile plus a JWT token pair."""

    serializer_class = RegisterInputSerializer
    throttle_classes = [RegistrationRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(**serializer.validated_data)

        data = UserOutputSerializer(user).data
        data.update(generate_jwt_token_for_user(user))
        return Response(data, status=status.HTTP_201_CREATED)
