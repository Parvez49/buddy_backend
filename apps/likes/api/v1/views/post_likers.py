from django.http import Http404
from rest_framework.generics import ListAPIView

from apps.likes.api.v1.serializers import LikerOutputSerializer
from apps.likes.selectors.like_selectors import get_post_likers
from apps.posts.selectors.post_selectors import get_post_for_user


class PostLikersListAPIView(ListAPIView):
    """Users who liked a post, most recent like first. Bounded/small list —
    page-number pagination (the project default), not cursor.
    """

    serializer_class = LikerOutputSerializer

    def get_queryset(self):
        post = get_post_for_user(post_id=self.kwargs["pk"], user=self.request.user)
        if post is None:
            raise Http404
        return get_post_likers(post=post)
