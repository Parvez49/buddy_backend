from django.urls import include, path

app_name = "chat"

urlpatterns = [
    path("v1/", include("apps.chat.api.v1.urls")),
]
