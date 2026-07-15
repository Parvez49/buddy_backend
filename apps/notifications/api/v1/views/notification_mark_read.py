from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.selectors.notification_selectors import get_notification_for_user
from apps.notifications.services.notification_services import mark_notification_read


class NotificationMarkReadAPIView(APIView):
    """POST: mark a single notification read. Idempotent — already-read is
    a no-op, 200 either way. A notification belonging to someone else 404s,
    same "don't confirm existence" rule as a private post.
    """

    def post(self, request, *args, **kwargs):
        notification = get_notification_for_user(notification_id=kwargs["pk"], user=request.user)
        if notification is None:
            raise Http404
        mark_notification_read(notification=notification)
        return Response(status=status.HTTP_200_OK)
