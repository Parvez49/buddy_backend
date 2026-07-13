from django.urls import path

from apps.comments.api.v1.views import (
    CommentListCreateAPIView,
    CommentReplyListCreateAPIView,
    CommentRetrieveUpdateDestroyAPIView,
)

app_name = "v1"

urlpatterns = [
    path(
        "posts/<uuid:post_id>/comments/",
        CommentListCreateAPIView.as_view(),
        name="comment-list-create",
    ),
    path(
        "comments/<uuid:comment_id>/replies/",
        CommentReplyListCreateAPIView.as_view(),
        name="comment-reply-list-create",
    ),
    path(
        "comments/<uuid:pk>/", CommentRetrieveUpdateDestroyAPIView.as_view(), name="comment-detail"
    ),
]
