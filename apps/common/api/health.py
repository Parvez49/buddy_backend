from django.core.cache import cache
from django.db import DatabaseError, connections
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.mixins import PublicAccessMixin


class LivenessAPIView(PublicAccessMixin, APIView):
    """Process is up and serving requests. No dependency checks — a
    container orchestrator restarts the process if this stops responding.
    """

    def get(self, request):
        return Response({"status": "ok"})


class ReadinessAPIView(PublicAccessMixin, APIView):
    """Process is up *and* able to serve real traffic — checks the
    dependencies a request actually needs. An orchestrator stops routing
    traffic here (without restarting the container) if this fails.
    """

    def get(self, request):
        checks = {"database": self._check_database(), "cache": self._check_cache()}
        ready = all(checks.values())
        return Response(
            {"status": "ok" if ready else "unavailable", "checks": checks},
            status=200 if ready else 503,
        )

    def _check_database(self) -> bool:
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
        except DatabaseError:
            return False
        return True

    def _check_cache(self) -> bool:
        try:
            cache.set("health_check", "ok", timeout=5)
            return cache.get("health_check") == "ok"
        except Exception:
            return False
