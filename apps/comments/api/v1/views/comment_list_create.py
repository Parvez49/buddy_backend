from django.http import Http404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from apps.comments.api.v1.serializers import CommentCreateInputSerializer, CommentOutputSerializer
from apps.comments.filters import CommentFilter
from apps.comments.selectors.comment_selectors import get_post_comments
from apps.comments.services.comment_services import comment_create
from apps.common.api.pagination import FeedCursorPagination
from apps.posts.models import Post
from apps.posts.selectors.post_selectors import get_post_for_user


class CommentListCreateAPIView(ListCreateAPIView):
    """GET: top-level comments on a post, newest first. POST: create a
    top-level comment on the post.

    A private post owned by someone else 404s here rather than 403ing —
    same visibility rule as the post detail view.
    """

    pagination_class = FeedCursorPagination
    filterset_class = CommentFilter

    def get_post(self) -> Post:
        post = get_post_for_user(post_id=self.kwargs["post_id"], user=self.request.user)
        if post is None:
            raise Http404
        return post

    def get_queryset(self):
        return get_post_comments(post=self.get_post())

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateInputSerializer
        return CommentOutputSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = comment_create(
            author=request.user, post=self.get_post(), **serializer.validated_data
        )

        return Response(CommentOutputSerializer(comment).data, status=status.HTTP_201_CREATED)
