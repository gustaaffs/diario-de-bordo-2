#!/usr/bin/env sh
set -e

echo "==> Waiting DB..."
python - <<'PY'
import os, time
import psycopg2

host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
name = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
pwd  = os.getenv("POSTGRES_PASSWORD")

for i in range(60):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=name, user=user, password=pwd)
        conn.close()
        print("DB OK")
        break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("DB not ready")
PY

echo "==> Migrate..."
python manage.py migrate --noinput

echo "==> Collectstatic..."
python manage.py collectstatic --noinput

echo "==> Start Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --log-level info

