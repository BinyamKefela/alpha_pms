python manage.py collectstatic --noinput
python manage.py migrate 
python -m gunicorn --bin 0.0.0.0:8000 --workers 3 alphapms.wsgi.py