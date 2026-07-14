from django.db import models

from apps.accounts.models import User
from apps.common.models import UUIDTimeStampedModel
from apps.posts.choices import MediaType, PostVisibility


class Post(UUIDTimeStampedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    text = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=20, choices=PostVisibility.choices, default=PostVisibility.PUBLIC
    )

    # Set only by post_update() when the author actually edits text/media.
    # Deliberately distinct from `updated_at`, which fires on *any* save
    # (e.g. a future Celery image re-encode) — that isn't an "edit" from the
    # author's point of view and shouldn't show as one.
    edited_at = models.DateTimeField(null=True, blank=True)

    # Denormalized — maintained via F() inside the same transaction as the
    # underlying reaction/comment. A user holds at most one reaction
    # (like/dislike, see apps.reactions), so these two never both move for
    # the same event — see reaction_services.post_react().
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    class Meta(UUIDTimeStampedModel.Meta):
        indexes = [
            # Cursor pagination needs a total order — created_at alone isn't
            # unique, id is the tiebreaker so ties can't duplicate/skip pages.
            models.Index(fields=["-created_at", "-id"], name="post_feed_idx"),
            # "This user's own posts, newest first."
            models.Index(fields=["author", "-created_at"], name="post_author_created_idx"),
            # Partial index: the feed reads public posts overwhelmingly more
            # than private ones — smaller index, stays hotter in cache.
            models.Index(
                fields=["-created_at", "-id"],
                name="post_public_feed_idx",
                condition=models.Q(visibility=PostVisibility.PUBLIC),
            ),
        ]

    def __str__(self) -> str:
        return f"Post({self.pk}) by {self.author_id}"


class PostMedia(UUIDTimeStampedModel):
    """One image or video attached to a post. A post can have several,
    ordered by `order` (the order the author uploaded/arranged them in).
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="posts/media/")
    media_type = models.CharField(max_length=10, choices=MediaType.choices)
    order = models.PositiveSmallIntegerField(default=0)

    # Populated for images at upload time (Pillow).
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    file_size = models.PositiveBigIntegerField()
    mime_type = models.CharField(max_length=100)

    class Meta(UUIDTimeStampedModel.Meta):
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["post", "order"], name="postmedia_post_order_idx"),
        ]

    def __str__(self) -> str:
        return f"PostMedia({self.pk}) on Post({self.post_id})"
