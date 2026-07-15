from django.http import Http404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from apps.accounts.models import User
from apps.chat.api.v1.serializers import (
    ConversationOutputSerializer,
    ConversationStartInputSerializer,
)
from apps.chat.selectors.chat_selectors import get_conversations
from apps.chat.services.chat_services import get_or_create_conversation
from apps.common.api.pagination import FeedCursorPagination


class ConversationListCreateAPIView(ListCreateAPIView):
    """GET: my conversations, most recently active first. POST: start (or
    fetch the existing) conversation with `{"participant": "<uuid>"}` — any
    registered user, no friend-request gating. Idempotent, same
    201-first-time/200-if-exists shape as `PostReactionAPIView`.
    """

    pagination_class = FeedCursorPagination

    def get_queryset(self):
        return get_conversations(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ConversationStartInputSerializer
        return ConversationOutputSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        other = User.objects.filter(pk=serializer.validated_data["participant"]).first()
        if other is None:
            raise Http404

        conversation, created = get_or_create_conversation(user=request.user, other=other)
        output = ConversationOutputSerializer(conversation, context={"request": request})
        return Response(
            output.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
