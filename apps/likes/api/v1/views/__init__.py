from apps.likes.api.v1.views.comment_like import CommentLikeAPIView
from apps.likes.api.v1.views.comment_likers import CommentLikersListAPIView
from apps.likes.api.v1.views.post_like import PostLikeAPIView
from apps.likes.api.v1.views.post_likers import PostLikersListAPIView

__all__ = [
    "PostLikeAPIView",
    "PostLikersListAPIView",
    "CommentLikeAPIView",
    "CommentLikersListAPIView",
]
