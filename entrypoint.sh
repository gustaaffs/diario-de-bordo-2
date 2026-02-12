#!/bin/sh
set -e

echo "Aguardando Postgres..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Postgres OK"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120