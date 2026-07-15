from django.urls import include, path

app_name = "notifications"

urlpatterns = [
    path("v1/", include("apps.notifications.api.v1.urls")),
]
