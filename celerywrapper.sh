#!/bin/bash
python manage.py celery worker --pidfile=/tmp/celeryd.pid -l info &
python manage.py celery beat --pidfile=/tmp/beat.pid -l info &
