from django.http import Http404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from apps.chat.api.v1.serializers import MessageCreateInputSerializer, MessageOutputSerializer
from apps.chat.selectors.chat_selectors import get_conversation_for_user, get_messages
from apps.chat.services.chat_services import message_send
from apps.common.api.pagination import FeedCursorPagination


class ConversationMessageListCreateAPIView(ListCreateAPIView):
    """GET: message history for a conversation, newest first. POST: send a
    message — real-time delivery to the other participant is pushed over
    `apps.chat.consumers.ChatConsumer`, not this response. A conversation
    the caller isn't part of 404s, same "don't confirm existence" rule as
    a private post.
    """

    pagination_class = FeedCursorPagination

    def get_conversation(self):
        conversation = get_conversation_for_user(
            conversation_id=self.kwargs["pk"], user=self.request.user
        )
        if conversation is None:
            raise Http404
        return conversation

    def get_queryset(self):
        return get_messages(conversation=self.get_conversation())

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MessageCreateInputSerializer
        return MessageOutputSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = message_send(
            conversation=self.get_conversation(),
            sender=request.user,
            text=serializer.validated_data["text"],
        )
        return Response(MessageOutputSerializer(message).data, status=status.HTTP_201_CREATED)
