import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.chat.selectors.chat_selectors import get_conversation_for_user, get_other_participant


class ChatConsumer(AsyncWebsocketConsumer):
    """One socket per user, not per conversation — joins `user-{id}-chat`
    on connect and receives `message.new` pushes for every conversation
    they're part of, including ones not currently open (for unread
    badges). Sending a message still goes through the REST API — same
    push-only principle as `apps.notifications.consumers.NotificationConsumer`.

    The one exception is `typing`: it's never persisted, so relaying it
    directly over the socket isn't a "write" the service layer needs to
    own. The target conversation is still looked up and ownership-checked
    server-side — never trust a client-supplied recipient id, or any
    connected user could spam typing events at anyone.
    """

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return
        self.user = user
        self.group_name = f"user-{user.id}-chat"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except TypeError, ValueError:
            return

        if data.get("action") == "typing":
            await self._relay_typing(data.get("conversation_id"))

    async def _relay_typing(self, conversation_id):
        if not conversation_id:
            return
        other_participant_id = await self._get_other_participant_id(conversation_id)
        if other_participant_id is None:
            return
        await self.channel_layer.group_send(
            f"user-{other_participant_id}-chat",
            {
                "type": "typing.push",
                "conversation_id": str(conversation_id),
                "user_id": str(self.user.id),
            },
        )

    @database_sync_to_async
    def _get_other_participant_id(self, conversation_id):
        conversation = get_conversation_for_user(conversation_id=conversation_id, user=self.user)
        if conversation is None:
            return None
        return get_other_participant(conversation=conversation, user=self.user).id

    async def message_new(self, event):
        """Handles the `message.new` group_send from apps.chat.tasks.push_message."""
        await self.send(text_data=json.dumps({"type": "message", "message": event["message"]}))

    async def typing_push(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing",
                    "conversation_id": event["conversation_id"],
                    "user_id": event["user_id"],
                }
            )
        )
