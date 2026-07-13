from django.urls import path

from apps.posts.api.v1.views import PostListCreateAPIView, PostRetrieveUpdateDestroyAPIView

app_name = "v1"

urlpatterns = [
    path("posts/", PostListCreateAPIView.as_view(), name="post-list-create"),
    path("posts/<uuid:pk>/", PostRetrieveUpdateDestroyAPIView.as_view(), name="post-detail"),
]
