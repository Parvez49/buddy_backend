from .base import *

# Must be first in INSTALLED_APPS (before django.contrib.staticfiles) so
# `runserver` picks up Daphne's ASGI-aware dev server — otherwise it's
# plain WSGI runserver and every websocket handshake fails with 1006.
# `daphne` is a main dependency (the docker-compose `websocket` service
# invokes it directly against config.asgi:application) — this hook is only
# what makes *local* `runserver` use it too, so local dev doesn't need a
# second process just to test a websocket.
INSTALLED_APPS = ["daphne", *INSTALLED_APPS]

# https://docs.djangoproject.com/en/dev/ref/settings/
DEBUG = env.bool("DJANGO_DEBUG", True)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="my-secret-key")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*", "localhost", "0.0.0.0", "127.0.0.1"])

# Base URL for building absolute media URLs in local development.
# Override via SITE_URL env var or change the port to match your runserver port.
SITE_URL = env("SITE_URL", default="http://192.168.0.109:8000")

# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        # Disable profiling panel due to an issue with Python 3.12:
        # https://github.com/jazzband/django-debug-toolbar/issues/1875
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

# https://docs.celeryq.dev/en/stable/userguide/configuration.html
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# For development, emails will be printed to the console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
