from django.http import Http404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.comments.api.v1.serializers import CommentOutputSerializer, CommentUpdateInputSerializer
from apps.comments.permissions import IsOwner
from apps.comments.selectors.comment_selectors import get_comment_for_user
from apps.comments.services.comment_services import comment_delete, comment_update


class CommentRetrieveUpdateDestroyAPIView(GenericAPIView):
    """Retrieve, update, or delete a single comment or reply — the same
    unified resource, since a reply is just a `Comment` with `parent` set.

    A comment on a private post owned by someone else 404s here rather
    than 403ing, mirroring the post detail view's visibility rule.
    """

    permission_classes = [IsOwner]

    def get_object(self):
        comment = get_comment_for_user(comment_id=self.kwargs["pk"], user=self.request.user)
        if comment is None:
            raise Http404
        self.check_object_permissions(self.request, comment)
        return comment

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return CommentUpdateInputSerializer
        return CommentOutputSerializer

    def get(self, request, *args, **kwargs):
        return Response(CommentOutputSerializer(self.get_object()).data)

    def patch(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        comment = comment_update(comment=comment, **serializer.validated_data)

        return Response(CommentOutputSerializer(comment).data)

    def delete(self, request, *args, **kwargs):
        comment_delete(comment=self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)
