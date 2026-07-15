from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.selectors.chat_selectors import get_conversation_for_user
from apps.chat.services.chat_services import mark_conversation_read


class ConversationMarkReadAPIView(APIView):
    """POST: mark every message from the other participant read.
    Idempotent, thread-level (not per-message) — matches real chat UX.
    """

    def post(self, request, *args, **kwargs):
        conversation = get_conversation_for_user(conversation_id=kwargs["pk"], user=request.user)
        if conversation is None:
            raise Http404
        marked_read = mark_conversation_read(conversation=conversation, user=request.user)
        return Response({"marked_read": marked_read}, status=status.HTTP_200_OK)
