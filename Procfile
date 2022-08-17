web: gunicorn mysite.wsgi --log-file -
web: gunicorn djangoproject.wsgi:application --log-file - --log-level debug
python manage.py collectstatic --noinput
manage.py migrate
