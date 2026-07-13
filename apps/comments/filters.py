import django_filters

from apps.comments.models import Comment


class CommentFilter(django_filters.FilterSet):
    author = django_filters.UUIDFilter(field_name="author_id")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Comment
        fields = ["author", "created_after", "created_before"]
