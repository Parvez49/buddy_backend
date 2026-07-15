from rest_framework.generics import ListAPIView

from apps.common.api.pagination import FeedCursorPagination
from apps.notifications.api.v1.serializers import NotificationOutputSerializer
from apps.notifications.filters import NotificationFilter
from apps.notifications.selectors.notification_selectors import get_notifications


class NotificationListAPIView(ListAPIView):
    """The caller's notifications, newest first. `?is_read=false` narrows
    to unread only; `?notification_type=comment` to a single type.
    """

    serializer_class = NotificationOutputSerializer
    pagination_class = FeedCursorPagination
    filterset_class = NotificationFilter

    def get_queryset(self):
        return get_notifications(user=self.request.user)
