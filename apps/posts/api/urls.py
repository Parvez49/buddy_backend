from django.urls import include, path

app_name = "posts"

urlpatterns = [
    path("v1/", include("apps.posts.api.v1.urls")),
]
