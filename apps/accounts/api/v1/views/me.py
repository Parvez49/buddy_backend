from rest_framework.generics import RetrieveAPIView

from apps.accounts.api.v1.serializers import UserOutputSerializer
from apps.accounts.models import User


class CurrentUserAPIView(RetrieveAPIView):
    """Return the authenticated user's own profile."""

    serializer_class = UserOutputSerializer

    def get_object(self) -> User:
        return self.request.user
