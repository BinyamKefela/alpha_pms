#!/bin/bash

# entrypoint.prod.sh
echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
gunicorn alpha_pms.wsgi:application --bind 0.0.0.0:8000
