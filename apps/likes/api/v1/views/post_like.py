from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.likes.services.like_services import post_like, post_unlike
from apps.posts.models import Post
from apps.posts.selectors.post_selectors import get_post_for_user


class PostLikeAPIView(APIView):
    """POST: like a post — idempotent (201 first time, 200 if already liked).
    DELETE: unlike — idempotent (204 either way, including a never-liked post).

    A private post owned by someone else 404s here rather than 403ing, same
    visibility rule as the post detail view.
    """

    def get_post(self) -> Post:
        post = get_post_for_user(post_id=self.kwargs["pk"], user=self.request.user)
        if post is None:
            raise Http404
        return post

    def post(self, request, *args, **kwargs):
        _, created = post_like(user=request.user, post=self.get_post())
        return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        post_unlike(user=request.user, post=self.get_post())
        return Response(status=status.HTTP_204_NO_CONTENT)
