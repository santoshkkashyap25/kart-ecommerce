#!/bin/sh

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Seeding data..."
python manage.py seed_data

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser already exists."
fi

PORT="${PORT:-8000}"
echo "Starting Gunicorn on port $PORT..."
exec gunicorn kart.wsgi:application --bind "0.0.0.0:$PORT" --workers 2 --timeout 120
