from django.core.management.base import BaseCommand
from karmaworld.apps.notes.models import *
from karmaworld.apps.courses.models import *

class Command(BaseCommand):
    help = """Set the field file_count on every Course and School
            to the correct value."""

    def handle(self, *args, **kwargs):
        for c in Course.objects.all():
            c.update_note_count()
            print "Updated course {c}".format(c=c)

        for s in School.objects.all():
            s.update_note_count()
            print "Updated school {s}".format(s=s)


