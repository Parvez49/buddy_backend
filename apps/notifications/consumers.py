import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """Push-only: the server notifies the client of new notifications in
    real time. All state changes (mark read, mark all read) go through the
    REST API, not this socket — one write path, consistent with the rest
    of the project's View -> Service -> Selector layering.
    """

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return
        self.group_name = f"user-{user.id}-notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_push(self, event):
        """Handles the `notification.push` group_send from
        `apps.notifications.tasks.push_notification`.
        """
        await self.send(
            text_data=json.dumps({"type": "notification", "notification": event["notification"]})
        )
