web: newrelic-admin run-program gunicorn -b 0.0.0.0:$PORT karmaworld.wsgi
worker: python manage.py celery worker -B -l info -Q $CELERY_QUEUE_NAME
