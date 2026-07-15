from django.urls import path

from apps.notifications.api.v1.views import (
    NotificationListAPIView,
    NotificationMarkAllReadAPIView,
    NotificationMarkReadAPIView,
    NotificationUnreadCountAPIView,
)

app_name = "v1"

urlpatterns = [
    path("notifications/", NotificationListAPIView.as_view(), name="notification-list"),
    path(
        "notifications/unread-count/",
        NotificationUnreadCountAPIView.as_view(),
        name="notification-unread-count",
    ),
    path(
        "notifications/read-all/",
        NotificationMarkAllReadAPIView.as_view(),
        name="notification-mark-all-read",
    ),
    path(
        "notifications/<uuid:pk>/read/",
        NotificationMarkReadAPIView.as_view(),
        name="notification-mark-read",
    ),
]
