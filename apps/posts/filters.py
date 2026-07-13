import django_filters

from apps.posts.choices import PostVisibility
from apps.posts.models import Post


class PostFilter(django_filters.FilterSet):
    visibility = django_filters.ChoiceFilter(choices=PostVisibility.choices)
    author = django_filters.UUIDFilter(field_name="author_id")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Post
        fields = ["visibility", "author", "created_after", "created_before"]
