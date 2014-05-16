web: gunicorn karmaworld.wsgi
celeryworker: python manage.py celery worker --pidfile=/tmp/celeryd.pid -l info
celerybeat: python manage.py celery beat --pidfile=/tmp/beat.pid -l info
tweetnote: python manage.py tweet_note
mturkresults: python manage.py get_mturk_results
