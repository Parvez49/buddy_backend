from django.urls import path

from apps.reactions.api.v1.views import (
    CommentReactionAPIView,
    CommentReactorsListAPIView,
    PostReactionAPIView,
    PostReactorsListAPIView,
)

app_name = "v1"

urlpatterns = [
    path("posts/<uuid:pk>/reaction/", PostReactionAPIView.as_view(), name="post-reaction"),
    path("posts/<uuid:pk>/reactions/", PostReactorsListAPIView.as_view(), name="post-reactors"),
    path("comments/<uuid:pk>/reaction/", CommentReactionAPIView.as_view(), name="comment-reaction"),
    path(
        "comments/<uuid:pk>/reactions/",
        CommentReactorsListAPIView.as_view(),
        name="comment-reactors",
    ),
]
