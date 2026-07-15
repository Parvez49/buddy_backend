from django.db import transaction
from django.db.models import F

from apps.accounts.models import User
from apps.comments.models import Comment
from apps.notifications.choices import NotificationType
from apps.notifications.services.notification_services import notification_create
from apps.posts.models import Post
from apps.reactions.choices import ReactionType
from apps.reactions.models import CommentReaction, PostReaction

_COUNTER_FIELD: dict[str, str] = {
    ReactionType.LIKE: "likes_count",
    ReactionType.DISLIKE: "dislikes_count",
}


@transaction.atomic
def post_react(*, user: User, post: Post, reaction_type: str) -> tuple[PostReaction, bool]:
    """Set `user`'s reaction to `post` to `reaction_type`. Idempotent:
    reacting with the same type twice is a no-op. Switching type (e.g.
    like -> dislike) moves the row's `reaction_type` in place and shifts one
    count from the old counter to the new one, inside this transaction.

    `select_for_update()` locks the row (if any) before the switch decision
    is made, so two concurrent switches on the same reaction resolve
    serially instead of double-counting; a first-time react still resolves
    the create/create race the way `get_or_create` always has — the
    retry-on-`IntegrityError` path re-runs `get()` against this same locked
    queryset.
    """
    reaction, created = PostReaction.objects.select_for_update().get_or_create(
        user=user, post=post, defaults={"reaction_type": reaction_type}
    )
    if created:
        Post.objects.filter(pk=post.pk).update(
            **{_COUNTER_FIELD[reaction_type]: F(_COUNTER_FIELD[reaction_type]) + 1}
        )
        # Only on first react, not a type switch — one notification per
        # reactor per post, not one per like<->dislike flip.
        notification_create(
            recipient=post.author,
            actor=user,
            notification_type=NotificationType.POST_REACTION,
            post=post,
        )
    elif reaction.reaction_type != reaction_type:
        old_type = reaction.reaction_type
        reaction.reaction_type = reaction_type
        reaction.save(update_fields=["reaction_type", "updated_at"])
        Post.objects.filter(pk=post.pk).update(
            **{
                _COUNTER_FIELD[old_type]: F(_COUNTER_FIELD[old_type]) - 1,
                _COUNTER_FIELD[reaction_type]: F(_COUNTER_FIELD[reaction_type]) + 1,
            }
        )
    return reaction, created


@transaction.atomic
def post_unreact(*, user: User, post: Post) -> bool:
    """Remove `user`'s reaction to `post`, if any. Idempotent: removing a
    reaction that was never made is a no-op, not an error.
    """
    reaction = PostReaction.objects.select_for_update().filter(user=user, post=post).first()
    if reaction is None:
        return False
    reaction_type = reaction.reaction_type
    reaction.delete()
    Post.objects.filter(pk=post.pk).update(
        **{_COUNTER_FIELD[reaction_type]: F(_COUNTER_FIELD[reaction_type]) - 1}
    )
    return True


@transaction.atomic
def comment_react(
    *, user: User, comment: Comment, reaction_type: str
) -> tuple[CommentReaction, bool]:
    """Like `post_react`, but for a comment (or reply)."""
    reaction, created = CommentReaction.objects.select_for_update().get_or_create(
        user=user, comment=comment, defaults={"reaction_type": reaction_type}
    )
    if created:
        Comment.objects.filter(pk=comment.pk).update(
            **{_COUNTER_FIELD[reaction_type]: F(_COUNTER_FIELD[reaction_type]) + 1}
        )
        notification_create(
            recipient=comment.author,
            actor=user,
            notification_type=NotificationType.COMMENT_REACTION,
            comment=comment,
        )
    elif reaction.reaction_type != reaction_type:
        old_type = reaction.reaction_type
        reaction.reaction_type = reaction_type
        reaction.save(update_fields=["reaction_type", "updated_at"])
        Comment.objects.filter(pk=comment.pk).update(
            **{
                _COUNTER_FIELD[old_type]: F(_COUNTER_FIELD[old_type]) - 1,
                _COUNTER_FIELD[reaction_type]: F(_COUNTER_FIELD[reaction_type]) + 1,
            }
        )
    return reaction, created


@transaction.atomic
def comment_unreact(*, user: User, comment: Comment) -> bool:
    """Like `post_unreact`, but for a comment (or reply)."""
    reaction = (
        CommentReaction.objects.select_for_update().filter(user=user, comment=comment).first()
    )
    if reaction is None:
        return False
    reaction_type = reaction.reaction_type
    reaction.delete()
    Comment.objects.filter(pk=comment.pk).update(
        **{_COUNTER_FIELD[reaction_type]: F(_COUNTER_FIELD[reaction_type]) - 1}
    )
    return True
