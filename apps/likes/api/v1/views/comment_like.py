from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.comments.models import Comment
from apps.comments.selectors.comment_selectors import get_comment_for_user
from apps.likes.services.like_services import comment_like, comment_unlike


class CommentLikeAPIView(APIView):
    """POST: like a comment or reply — idempotent (201 first time, 200 if
    already liked). DELETE: unlike — idempotent (204 either way).

    Visibility follows the comment's post — 404, not 403, if it isn't
    visible to the requester.
    """

    def get_comment(self) -> Comment:
        comment = get_comment_for_user(comment_id=self.kwargs["pk"], user=self.request.user)
        if comment is None:
            raise Http404
        return comment

    def post(self, request, *args, **kwargs):
        _, created = comment_like(user=request.user, comment=self.get_comment())
        return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        comment_unlike(user=request.user, comment=self.get_comment())
        return Response(status=status.HTTP_204_NO_CONTENT)
