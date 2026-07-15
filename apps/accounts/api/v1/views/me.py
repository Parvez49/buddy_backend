from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.accounts.api.v1.serializers import ProfileUpdateInputSerializer, UserOutputSerializer
from apps.accounts.models import User
from apps.accounts.services.user_services import user_update


class CurrentUserAPIView(GenericAPIView):
    """GET: the authenticated user's own profile. PATCH: update mutable
    profile fields (first_name, last_name, designation, avatar).
    """

    def get_object(self) -> User:
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ProfileUpdateInputSerializer
        return UserOutputSerializer

    def get(self, request, *args, **kwargs):
        return Response(UserOutputSerializer(self.get_object()).data)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = user_update(user=self.get_object(), **serializer.validated_data)

        return Response(UserOutputSerializer(user).data)
