from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School

from celery import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@task(name="fix_note_counts")
def fix_note_counts():
    """
    Set the field file_count on every Course and School to the correct value.
    """

    for c in Course.objects.all():
        c.update_note_count()
        print "Updated course {c}".format(c=c)

    for s in School.objects.all():
        s.update_note_count()
        print "Updated school {s}".format(s=s)
