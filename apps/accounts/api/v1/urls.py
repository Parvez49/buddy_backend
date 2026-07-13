from django.urls import path

from apps.accounts.api.v1.views import (
    CurrentUserAPIView,
    GoogleAuthAPIView,
    LoginAPIView,
    LogoutAPIView,
    RegisterAPIView,
    TokenRefreshAPIView,
)

app_name = "v1"

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/google/", GoogleAuthAPIView.as_view(), name="google"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
    path("auth/token/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("auth/me/", CurrentUserAPIView.as_view(), name="me"),
]
