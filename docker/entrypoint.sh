#!/bin/sh
set -eu

# db/redis readiness is handled by docker-compose's `depends_on:
# condition: service_healthy` — by the time this runs, both are up.

if [ "$1" = "gunicorn" ]; then
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
fi

exec "$@"
