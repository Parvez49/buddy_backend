from django.http import Http404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.posts.api.v1.serializers import PostOutputSerializer, PostUpdateInputSerializer
from apps.posts.permissions import IsOwner
from apps.posts.selectors.post_selectors import get_post_for_user
from apps.posts.services.post_services import post_delete, post_update


class PostRetrieveUpdateDestroyAPIView(GenericAPIView):
    """Retrieve, update, or delete a single post.

    A private post owned by someone else 404s here rather than 403ing —
    `get_post_for_user` already filters it out of visibility, so there is
    nothing left to leak.
    """

    permission_classes = [IsOwner]

    def get_object(self):
        post = get_post_for_user(post_id=self.kwargs["pk"], user=self.request.user)
        if post is None:
            raise Http404
        self.check_object_permissions(self.request, post)
        return post

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return PostUpdateInputSerializer
        return PostOutputSerializer

    def get(self, request, *args, **kwargs):
        return Response(PostOutputSerializer(self.get_object()).data)

    def patch(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        post = post_update(post=post, **serializer.validated_data)

        return Response(PostOutputSerializer(post).data)

    def delete(self, request, *args, **kwargs):
        post_delete(post=self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)
