#!/bin/bash
python manage.py celery worker --pidfile=/tmp/celeryd.pid -l info -Q $CELERY_QUEUE_NAME &
sleep 5
workerpid=`cat /tmp/celeryd.pid`
echo "Started celery worker with pid $workerpid"
python manage.py celery beat --pidfile=/tmp/celerybeat.pid -l info &
sleep 5
beatpid=`cat /tmp/celerybeat.pid`
echo "Started celery beat with pid $beatpid"
wait $workerpid
wait $beatpid
