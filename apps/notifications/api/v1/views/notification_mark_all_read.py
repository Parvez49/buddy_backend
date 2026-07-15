from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.services.notification_services import mark_all_notifications_read


class NotificationMarkAllReadAPIView(APIView):
    """POST: mark every unread notification read. Idempotent."""

    def post(self, request, *args, **kwargs):
        marked_read = mark_all_notifications_read(user=request.user)
        return Response({"marked_read": marked_read})
