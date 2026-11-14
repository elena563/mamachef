#!/bin/bash
set -u

NGINX_PORT="${PORT:-8000}"

export MALLOC_ARENA_MAX="${MALLOC_ARENA_MAX:-2}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"

mkdir -p /tmp/nginx/client_body /tmp/nginx/proxy /tmp/nginx/fastcgi /tmp/nginx/uwsgi /tmp/nginx/scgi

sed "s/__PORT__/${NGINX_PORT}/g" /app/nginx.conf > /tmp/nginx.conf

if ! nginx -t -c /tmp/nginx.conf; then
    exit 1
fi

echo "Running database migrations..."
for attempt in 1 2 3 4 5; do
    if python manage.py migrate --noinput; then
        break
    fi

    if [ "$attempt" -eq 5 ]; then
        echo "Database migration failed" >&2
        exit 1
    fi

    echo "Migration failed, retrying in 5s..." >&2
    sleep 5
done

nginx -c /tmp/nginx.conf -g "daemon off;" &
NGINX_PID=$!

gunicorn mamachef.wsgi:application \
    --bind 127.0.0.1:8001 \
    --workers "${WEB_CONCURRENCY:-1}" \
    --timeout 120 \
    --forwarded-allow-ips=127.0.0.1 \
    --access-logfile - \
    --error-logfile - &
GUNICORN_PID=$!

SHUTDOWN=0

shutdown() {
    if [ "$SHUTDOWN" -eq 1 ]; then
        return
    fi

    SHUTDOWN=1
    trap - SIGTERM SIGINT
    kill -TERM "$GUNICORN_PID" 2>/dev/null || true
    kill -QUIT "$NGINX_PID" 2>/dev/null || true
    wait "$GUNICORN_PID" 2>/dev/null || true
    wait "$NGINX_PID" 2>/dev/null || true
}

trap shutdown SIGTERM SIGINT

wait -n "$NGINX_PID" "$GUNICORN_PID"
STATUS=$?

shutdown
exit "$STATUS"
