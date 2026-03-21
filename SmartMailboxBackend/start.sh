#!/bin/bash

set -e

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery Worker..."
    celery -A config worker -l info
elif [ "$SERVICE_TYPE" = "beat" ]; then
    echo "Starting Celery Beat..."
    celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
else
    echo "Starting Gunicorn..."
    gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
fi
