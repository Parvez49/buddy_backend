from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.comments.models import Comment
from apps.comments.selectors.comment_selectors import get_comment_for_user
from apps.reactions.api.v1.serializers import ReactionInputSerializer
from apps.reactions.services.reaction_services import comment_react, comment_unreact


class CommentReactionAPIView(APIView):
    """POST: react to a comment or reply with `reaction_type` (like/dislike)
    — idempotent (201 first time, 200 if already reacting the same way or
    switching type). DELETE: remove the reaction — idempotent (204 either
    way).

    Visibility follows the comment's post — 404, not 403, if it isn't
    visible to the requester.
    """

    def get_comment(self) -> Comment:
        comment = get_comment_for_user(comment_id=self.kwargs["pk"], user=self.request.user)
        if comment is None:
            raise Http404
        return comment

    def post(self, request, *args, **kwargs):
        serializer = ReactionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        _, created = comment_react(
            user=request.user,
            comment=self.get_comment(),
            reaction_type=serializer.validated_data["reaction_type"],
        )
        return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        comment_unreact(user=request.user, comment=self.get_comment())
        return Response(status=status.HTTP_204_NO_CONTENT)
