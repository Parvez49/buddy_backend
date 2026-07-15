from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.selectors.notification_selectors import get_unread_count


class NotificationUnreadCountAPIView(APIView):
    """GET: how many unread notifications the caller has — cheap enough to
    poll from a client badge without paginating the full list.
    """

    def get(self, request, *args, **kwargs):
        return Response({"unread_count": get_unread_count(user=request.user)})
