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

### Docker (staging)

```bash
cp .env.staging.example .env.staging          # fill in secrets — never commit this file
docker compose --env-file .env.staging -f docker-compose.staging.yml up -d --build
```

This brings up `db` (Postgres), `redis`, `web` (Gunicorn behind the
`config.settings.staging` module), `celery_worker`, `celery_beat`, and `nginx`
(reverse proxy on `:80`, serves `/static/` and `/media/` directly, proxies
everything else to `web`). `web`'s entrypoint (`docker/entrypoint.sh`) runs
`migrate` and `collectstatic` before starting Gunicorn; `celery_beat` waits on
`web`'s healthcheck so it never schedules against an unmigrated schema.

`--env-file` is required on every `docker compose ... -f docker-compose.staging.yml`
invocation (not just `up`) — compose only reads `.env` by default for the
variable substitution used inside the compose file itself (`${POSTGRES_PASSWORD}`
etc.); `env_file: .env.staging` on each service only injects vars into the
*container*, which is a separate mechanism.

`.env.staging.example` ships with `DJANGO_SECURE_SSL_REDIRECT=False` because
this compose stack's `nginx` doesn't terminate TLS — flip it to `True` once a
real cert (or a TLS-terminating load balancer) sits in front, otherwise every
request redirect-loops against `X-Forwarded-Proto: http`.

Media currently persists to a local Docker volume (`media_volume`), not S3 —
`ARCHITECTURE.md` §15 lists `AWS_*`/`STORAGE_BACKEND` env vars but nothing in
the codebase consumes them yet; wiring `django-storages` is a follow-up.

Health checks (used by the `web` service's own healthcheck and suitable for
an external uptime check or orchestrator probe):

- `/health/live/` — process is up, no dependency checks
- `/health/ready/` — checks Postgres + Redis connectivity, `503` if either is down

### Zero-downtime migrations

Additive-first: a release that adds a column/table deploys cleanly against
old *and* new code running side by side during a rolling deploy. Never drop or
rename a column in the same release that stops writing to it — stop writing
first, deploy, confirm, then drop the column in a follow-up release. The same
applies to renames (add new + dual-write + backfill + stop writing old + drop
old, as separate releases), since `django_celery_beat`/`web`/`celery_worker`
run different code versions for the duration of a rolling deploy.

### Not yet built

Full Nginx/Gunicorn *hardening* (rate-limit tuning, `read_only` containers,
non-bind-mount volumes for prod), an S3/MinIO media backend, and a production
(`docker-compose.prod.yml`) variant remain open — this compose file targets
staging specifically, per `ARCHITECTURE.md` Phase 12.
