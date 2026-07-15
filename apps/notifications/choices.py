from django.db import models


class NotificationType(models.TextChoices):
    COMMENT = "comment", "Comment"
    REPLY = "reply", "Reply"
    POST_REACTION = "post_reaction", "Post Reaction"
    COMMENT_REACTION = "comment_reaction", "Comment Reaction"
