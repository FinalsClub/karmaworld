web: gunicorn karmaworld.wsgi
celeryworker: python manage.py celery worker --pidfile=/tmp/celeryd.pid -l info
celerybeat: python manage.py celery beat --pidfile=/tmp/beat.pid -l info
celerywrapper: sh celerywrapper.sh
