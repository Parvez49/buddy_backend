from django.urls import include, path

app_name = "comments"

urlpatterns = [
    path("v1/", include("apps.comments.api.v1.urls")),
]
