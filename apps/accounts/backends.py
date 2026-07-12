from django.contrib.auth.backends import ModelBackend

from apps.accounts.models import User


class EmailBackend(ModelBackend):
    """Authenticate a user by email and password."""

    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
