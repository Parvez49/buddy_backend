from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.accounts.api.v1.serializers import (
    GoogleAuthInputSerializer,
    UserOutputSerializer,
)
from apps.accounts.services.google_auth_services import verify_google_id_token
from apps.accounts.services.user_services import user_get_or_create_from_google
from apps.accounts.utils import generate_jwt_token_for_user
from apps.common.api.mixins import PublicAccessMixin
from apps.common.throttling import LoginRateThrottle


class GoogleAuthAPIView(PublicAccessMixin, GenericAPIView):
    """Sign in with Google.

    Registers the account on first sign-in — linking by Google-verified
    email — and logs in on every subsequent one, returning a JWT pair either
    way. 201 on first sign-in (account created), 200 otherwise.
    """

    serializer_class = GoogleAuthInputSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        claims = verify_google_id_token(id_token=serializer.validated_data["id_token"])
        user, created = user_get_or_create_from_google(
            email=claims["email"].lower(),
            first_name=claims.get("given_name", ""),
            last_name=claims.get("family_name", ""),
        )

        data = UserOutputSerializer(user).data
        data.update(generate_jwt_token_for_user(user))
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(data, status=status_code)
