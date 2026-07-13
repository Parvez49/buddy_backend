from django.urls import include, path

app_name = "likes"

urlpatterns = [
    path("v1/", include("apps.likes.api.v1.urls")),
]
