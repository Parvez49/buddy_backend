from django.urls import path

from apps.chat.api.v1.views import (
    ConversationListCreateAPIView,
    ConversationMarkReadAPIView,
    ConversationMessageListCreateAPIView,
)

app_name = "v1"

urlpatterns = [
    path(
        "chat/conversations/",
        ConversationListCreateAPIView.as_view(),
        name="conversation-list-create",
    ),
    path(
        "chat/conversations/<uuid:pk>/messages/",
        ConversationMessageListCreateAPIView.as_view(),
        name="conversation-messages",
    ),
    path(
        "chat/conversations/<uuid:pk>/read/",
        ConversationMarkReadAPIView.as_view(),
        name="conversation-mark-read",
    ),
]
