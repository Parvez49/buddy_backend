from django.contrib import admin

from apps.likes.models import CommentLike, PostLike


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__email",)


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "created_at")
    search_fields = ("user__email",)
