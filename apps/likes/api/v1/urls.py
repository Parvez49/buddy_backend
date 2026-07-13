from django.urls import path

from apps.likes.api.v1.views import (
    CommentLikeAPIView,
    CommentLikersListAPIView,
    PostLikeAPIView,
    PostLikersListAPIView,
)

app_name = "v1"

urlpatterns = [
    path("posts/<uuid:pk>/like/", PostLikeAPIView.as_view(), name="post-like"),
    path("posts/<uuid:pk>/likes/", PostLikersListAPIView.as_view(), name="post-likers"),
    path("comments/<uuid:pk>/like/", CommentLikeAPIView.as_view(), name="comment-like"),
    path("comments/<uuid:pk>/likes/", CommentLikersListAPIView.as_view(), name="comment-likers"),
]
