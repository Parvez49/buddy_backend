from rest_framework.generics import ListAPIView

from apps.accounts.api.v1.serializers import UserListOutputSerializer
from apps.accounts.selectors.user_selectors import get_users_excluding
from apps.common.api.pagination import StandardResultsSetPagination


class UserListAPIView(ListAPIView):
    """All other active users, alphabetical — there's no friends/follow
    concept yet, so every member sees every member. `?search=` matches
    first/last name (see `search_fields`).
    """

    serializer_class = UserListOutputSerializer
    pagination_class = StandardResultsSetPagination
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        return get_users_excluding(user=self.request.user)
