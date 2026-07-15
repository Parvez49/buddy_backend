import django_filters

from apps.notifications.choices import NotificationType
from apps.notifications.models import Notification


class NotificationFilter(django_filters.FilterSet):
    is_read = django_filters.BooleanFilter()
    notification_type = django_filters.ChoiceFilter(choices=NotificationType.choices)

    class Meta:
        model = Notification
        fields = ["is_read", "notification_type"]
