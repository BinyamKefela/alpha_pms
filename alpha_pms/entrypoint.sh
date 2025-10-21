#!/bin/sh

echo "Running migrations Bini"
python manage.py migrate

echo "starting server Bini"
python manage.py runserver 0.0.0.0:8000