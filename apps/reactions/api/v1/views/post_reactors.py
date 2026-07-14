from django.http import Http404
from rest_framework.generics import ListAPIView

from apps.posts.selectors.post_selectors import get_post_for_user
from apps.reactions.api.v1.serializers import ReactorOutputSerializer
from apps.reactions.filters import ReactionFilter
from apps.reactions.selectors.reaction_selectors import get_post_reactors


class PostReactorsListAPIView(ListAPIView):
    """Users who reacted to a post, most recent first. `?reaction_type=like`
    narrows to a single type (e.g. "who liked this"). Bounded/small list —
    page-number pagination (the project default), not cursor.
    """

    serializer_class = ReactorOutputSerializer
    filterset_class = ReactionFilter

    def get_queryset(self):
        post = get_post_for_user(post_id=self.kwargs["pk"], user=self.request.user)
        if post is None:
            raise Http404
        return get_post_reactors(post=post)
