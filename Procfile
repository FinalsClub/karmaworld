web: gunicorn karmaworld.wsgi
celery-worker: python manage.py celery worker --pidfile=/tmp/celeryd.pid -l info
celery-beat: python manage.py celery beat --pidfile=/tmp/beat.pid -l info
