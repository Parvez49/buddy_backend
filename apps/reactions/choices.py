from django.db import models


class ReactionType(models.TextChoices):
    LIKE = "like", "Like"
    DISLIKE = "dislike", "Dislike"
