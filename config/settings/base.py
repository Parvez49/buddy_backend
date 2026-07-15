"""Base settings to build other settings files upon."""

from datetime import timedelta
from pathlib import Path

import environ

from apps.common.logging import configure_structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    # Provides channel layers, routing, consumers. Note: `channels` alone
    # does NOT make `runserver` ASGI/websocket-aware — that override comes
    # from the separate `daphne` app, added first in settings/local.py
    # (it's a dev-only dependency; production runs a real ASGI server).
    "channels",
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    # Third-party apps
    "corsheaders",
    "django_celery_beat",
    "django_celery_results",
    "django_filters",
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # Local Apps
    "apps.accounts",
    "apps.common",
    "apps.posts",
    "apps.comments",
    "apps.reactions",
    "apps.notifications",
    "apps.chat",
]

# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.common.middleware.RequestIDMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Security Settings
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-content-type-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-samesite
SESSION_COOKIE_SAMESITE = "Lax"
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-samesite
CSRF_COOKIE_SAMESITE = "Lax"

# https://docs.djangoproject.com/en/dev/ref/settings/#databases
# DATABASES = {'default': env.db('DATABASE_URL')}
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)

# https://docs.djangoproject.com/en/dev/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = [str(BASE_DIR / "fixtures")]

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
# Custom user model
AUTH_USER_MODEL = "accounts.User"

# https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#specifying-authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "apps.accounts.backends.EmailBackend",
]

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
# Argon2 is OWASP's current recommendation; listed first so it becomes the
# hasher for new/changed passwords. The rest stay so existing hashes made
# with them (e.g. fixtures, migrations) still verify.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# https://docs.djangoproject.com/en/dev/topics/i18n/
USE_TZ = True
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
LANGUAGE_CODE = "en-us"

# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"

# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# https://docs.djangoproject.com/en/dev/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# https://channels.readthedocs.io/en/latest/topics/channel_layers.html
# Backs apps.notifications' real-time push (config/routing.py, config/middleware.py).
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                env(
                    "CHANNEL_REDIS_URL",
                    default=env("REDIS_URL", default="redis://127.0.0.1:6379/0"),
                )
            ],
        },
    }
}

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"

MEDIA_ROOT = str(BASE_DIR / "media")
MEDIA_URL = "/media/"

# https://docs.djangoproject.com/en/dev/ref/files/uploads/
MAX_IMAGE_UPLOAD_SIZE_MB = env.int("MAX_IMAGE_UPLOAD_SIZE_MB", default=5)
MAX_VIDEO_UPLOAD_SIZE_MB = env.int("MAX_VIDEO_UPLOAD_SIZE_MB", default=50)

# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Structured JSON logging in prod/staging, human-readable console in dev.
# request_id (bound by RequestIDMiddleware) is attached to every log line.
configure_structlog(
    json_logs=env("LOG_FORMAT", default="console") == "json",
    log_level=env("LOG_LEVEL", default="INFO"),
)

# https://docs.celeryq.dev/en/stable/userguide/configuration.html
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # JWT only — this is a stateless JSON API, not a browser session app.
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": (
        # JSON-only API — no BrowsableAPIRenderer, no HTML rendering surface.
        "apps.common.api.renderers.EnvelopeJSONRenderer",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.common.api.pagination.StandardResultsSetPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "login": "10/minute",
    },
    "EXCEPTION_HANDLER": "apps.common.api.exceptions.custom_exception_handler",
}

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=15)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=env("DJANGO_SECRET_KEY", default="fallback-key")),
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"
if env.bool("CORS_ALLOW_ALL_ORIGINS", default=False):
    if not DEBUG and env("DJANGO_SETTINGS_MODULE") == "config.settings.production":
        raise ValueError("CORS_ALLOW_ALL_ORIGINS cannot be True in production")
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # If not allowing all origins, use CORS_ALLOWED_ORIGINS
    CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    "TITLE": "Backend API",
    "DESCRIPTION": "API documentation for the backend project.",
    "VERSION": "1.0.0",
    # 'SCHEMA_PATH_PREFIX': '/api/v[0-9]',
    "COMPONENT_SPLIT_REQUEST": True,
    # Every response is wrapped by EnvelopeJSONRenderer before it reaches the
    # client — without this hook the schema documents the unwrapped body.
    "POSTPROCESSING_HOOKS": ["apps.common.api.schema.envelope_postprocessing_hook"],
}

FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")

# https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
# Client IDs (web + mobile, as needed) allowed as the `aud` claim on a
# Google ID token. Unset/empty means every Google sign-in attempt is
# rejected at the audience check — safe default, not a hard failure.
GOOGLE_OAUTH_CLIENT_IDS = env.list("GOOGLE_OAUTH_CLIENT_IDS", default=[])
