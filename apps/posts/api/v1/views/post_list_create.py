from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from apps.common.api.pagination import FeedCursorPagination
from apps.posts.api.v1.serializers import PostCreateInputSerializer, PostOutputSerializer
from apps.posts.filters import PostFilter
from apps.posts.selectors.post_selectors import get_feed_posts
from apps.posts.services.post_services import post_create


class PostListCreateAPIView(ListCreateAPIView):
    """GET: the feed (PUBLIC posts + the caller's own PRIVATE ones), newest
    first. POST: create a post.
    """

    pagination_class = FeedCursorPagination
    filterset_class = PostFilter
    search_fields = ["text"]

    def get_queryset(self):
        return get_feed_posts(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateInputSerializer
        return PostOutputSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = post_create(author=request.user, **serializer.validated_data)

        return Response(PostOutputSerializer(post).data, status=status.HTTP_201_CREATED)
