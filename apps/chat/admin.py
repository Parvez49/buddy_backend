from django.contrib import admin

from apps.chat.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "text", "is_read", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "participant_one", "participant_two", "last_message_at")
    search_fields = ("participant_one__email", "participant_two__email")
    readonly_fields = ("last_message_at", "last_message_preview", "created_at", "updated_at")
    inlines = [MessageInline]
