from django.http import Http404
from rest_framework.generics import ListAPIView

from apps.comments.selectors.comment_selectors import get_comment_for_user
from apps.reactions.api.v1.serializers import ReactorOutputSerializer
from apps.reactions.filters import ReactionFilter
from apps.reactions.selectors.reaction_selectors import get_comment_reactors


class CommentReactorsListAPIView(ListAPIView):
    """Users who reacted to a comment or reply, most recent first.
    `?reaction_type=like` narrows to a single type.
    """

    serializer_class = ReactorOutputSerializer
    filterset_class = ReactionFilter

    def get_queryset(self):
        comment = get_comment_for_user(comment_id=self.kwargs["pk"], user=self.request.user)
        if comment is None:
            raise Http404
        return get_comment_reactors(comment=comment)
