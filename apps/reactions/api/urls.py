from django.urls import include, path

app_name = "reactions"

urlpatterns = [
    path("v1/", include("apps.reactions.api.v1.urls")),
]
