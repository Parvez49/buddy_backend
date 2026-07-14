from django.contrib import admin

from apps.reactions.models import CommentReaction, PostReaction


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "reaction_type", "created_at")
    list_filter = ("reaction_type",)
    search_fields = ("user__email",)


@admin.register(CommentReaction)
class CommentReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "reaction_type", "created_at")
    list_filter = ("reaction_type",)
    search_fields = ("user__email",)
