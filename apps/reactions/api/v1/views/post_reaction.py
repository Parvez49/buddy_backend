from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.models import Post
from apps.posts.selectors.post_selectors import get_post_for_user
from apps.reactions.api.v1.serializers import ReactionInputSerializer
from apps.reactions.services.reaction_services import post_react, post_unreact


class PostReactionAPIView(APIView):
    """POST: react to a post with `reaction_type` (like/dislike) — idempotent
    (201 first time, 200 if already reacting the same way or switching type).
    DELETE: remove the reaction — idempotent (204 either way, including a
    post the user never reacted to).

    A private post owned by someone else 404s here rather than 403ing, same
    visibility rule as the post detail view.
    """

    def get_post(self) -> Post:
        post = get_post_for_user(post_id=self.kwargs["pk"], user=self.request.user)
        if post is None:
            raise Http404
        return post

    def post(self, request, *args, **kwargs):
        serializer = ReactionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        _, created = post_react(
            user=request.user,
            post=self.get_post(),
            reaction_type=serializer.validated_data["reaction_type"],
        )
        return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        post_unreact(user=request.user, post=self.get_post())
        return Response(status=status.HTTP_204_NO_CONTENT)
