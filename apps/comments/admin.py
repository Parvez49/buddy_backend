from django.contrib import admin

from apps.comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "parent", "likes_count", "replies_count", "created_at")
    search_fields = ("text", "author__email")
    readonly_fields = ("likes_count", "replies_count", "created_at", "updated_at")
