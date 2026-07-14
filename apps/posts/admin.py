from django.contrib import admin

from apps.posts.models import Post, PostMedia


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 0
    readonly_fields = ("width", "height", "duration_seconds", "file_size", "mime_type")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "visibility",
        "likes_count",
        "dislikes_count",
        "comments_count",
        "created_at",
    )
    list_filter = ("visibility",)
    search_fields = ("text", "author__email")
    readonly_fields = (
        "likes_count",
        "dislikes_count",
        "comments_count",
        "edited_at",
        "created_at",
        "updated_at",
    )
    inlines = [PostMediaInline]
