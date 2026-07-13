from django.http import Http404
from rest_framework.generics import ListAPIView

from apps.comments.selectors.comment_selectors import get_comment_for_user
from apps.likes.api.v1.serializers import LikerOutputSerializer
from apps.likes.selectors.like_selectors import get_comment_likers


class CommentLikersListAPIView(ListAPIView):
    """Users who liked a comment or reply, most recent like first."""

    serializer_class = LikerOutputSerializer

    def get_queryset(self):
        comment = get_comment_for_user(comment_id=self.kwargs["pk"], user=self.request.user)
        if comment is None:
            raise Http404
        return get_comment_likers(comment=comment)
