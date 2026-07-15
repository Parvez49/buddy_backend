# Buddy Backend

A Django REST API for a social feed: posts (text/image/video), comments with
one-level replies, and like/dislike reactions on both. JWT auth (email/password
+ Google Sign-In). See `ARCHITECTURE.md` for design rationale and the full
phase-by-phase build plan; this file is just "how do I run it."

## Stack

Django 5.2 · Django REST Framework · PostgreSQL · Redis · Celery · JWT
(`djangorestframework-simplejwt`) · `drf-spectacular` (OpenAPI) · `uv` (deps)

## Development

```bash
uv sync                                          # install deps (main + dev group)

cp .env.example .env                             # fill in secrets; DATABASE_URL
                                                  # unset falls back to local sqlite

DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py createsuperuser
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
```

`manage.py` defaults to `config.settings.local`, so the `DJANGO_SETTINGS_MODULE`
prefix above is only needed if your shell doesn't already export it. `wsgi.py`
defaults to `production` — always set it explicitly outside local dev.

With the server running:

- Swagger UI — `http://localhost:8000/api/docs/`
- ReDoc — `http://localhost:8000/api/redoc/`
- Raw OpenAPI schema — `http://localhost:8000/api/schema/`
- Admin — `http://localhost:8000/admin/`

### Before committing

```bash
ruff check . && ruff format --check .
mypy .
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py makemigrations --check --dry-run
pytest --cov --cov-fail-under=85
bandit -r apps config
detect-secrets scan
```

### Adding dependencies

```bash
uv add <pkg>            # runtime
uv add --dev <pkg>       # dev-only
```

Never hand-edit `uv.lock`.

## Deployment

Three settings modules layer on top of `config/settings/base.py`:

- `config.settings.local` — sqlite fallback, debug toolbar, Celery eager mode
- `config.settings.staging`
- `config.settings.production` — adds HSTS + secure-cookie settings on top of staging

Set `DJANGO_SETTINGS_MODULE` explicitly for any non-local environment; there is
no implicit default outside `manage.py`. Required environment variables are
listed in `.env.example` and `ARCHITECTURE.md` §15 — the app raises on boot if
a required staging/production variable (e.g. `DJANGO_SECURE_SSL_REDIRECT`,
`EMAIL_HOST`) is missing.

The JWT blacklist (`rest_framework_simplejwt.token_blacklist`) is
PostgreSQL-backed, not Redis — run `flushexpiredtokens` on a schedule in
production or the blacklist table grows unbounded.

Containerization, Nginx, and Gunicorn hardening are tracked as Phase 12 in
`ARCHITECTURE.md` and aren't built yet — until then, run with Gunicorn
directly against `config.wsgi` behind whatever reverse proxy you're using.
