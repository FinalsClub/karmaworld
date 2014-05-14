web: gunicorn karmaworld.wsgi
celery: python manage.py celery worker --pidfile=/tmp/celeryd.pid -l info
