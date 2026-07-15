"""
URL configuration for buddy_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.common.api.health import LivenessAPIView, ReadinessAPIView

api_url_patterns = (
    [
        path("", include("apps.accounts.api.urls")),
        path("", include("apps.posts.api.urls")),
        path("", include("apps.comments.api.urls")),
        path("", include("apps.reactions.api.urls")),
        path("", include("apps.notifications.api.urls")),
    ],
    "api",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # health checks — polled by the container orchestrator, not versioned API
    path("health/live/", LivenessAPIView.as_view(), name="health-live"),
    path("health/ready/", ReadinessAPIView.as_view(), name="health-ready"),
    # api documentation
    path("api/schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # api
    path("api/", include(api_url_patterns)),
    path("api_auth/", include("rest_framework.urls")),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
