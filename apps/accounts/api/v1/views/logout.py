from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.v1.serializers import LogoutInputSerializer


class LogoutAPIView(APIView):
    """Blacklist the refresh token to effectively log the user out."""

    def post(self, request):
        serializer = LogoutInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_205_RESET_CONTENT)
