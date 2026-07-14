from django.http import Http404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from apps.comments.api.v1.serializers import CommentCreateInputSerializer, CommentOutputSerializer
from apps.comments.filters import CommentFilter
from apps.comments.models import Comment
from apps.comments.selectors.comment_selectors import get_comment_for_user, get_comment_replies
from apps.comments.services.comment_services import comment_create
from apps.common.api.pagination import ReplyCursorPagination


class CommentReplyListCreateAPIView(ListCreateAPIView):
    """GET: replies to a comment, oldest first. POST: create a reply (sets
    `parent` to the comment in the URL).

    Visibility follows the parent comment's post — 404, not 403, if it
    isn't visible to the requester.
    """

    pagination_class = ReplyCursorPagination
    filterset_class = CommentFilter

    def get_parent_comment(self) -> Comment:
        comment = get_comment_for_user(comment_id=self.kwargs["comment_id"], user=self.request.user)
        if comment is None:
            raise Http404
        return comment

    def get_queryset(self):
        return get_comment_replies(comment=self.get_parent_comment(), user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateInputSerializer
        return CommentOutputSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent = self.get_parent_comment()
        reply = comment_create(
            author=request.user, post=parent.post, parent=parent, **serializer.validated_data
        )

        return Response(CommentOutputSerializer(reply).data, status=status.HTTP_201_CREATED)
