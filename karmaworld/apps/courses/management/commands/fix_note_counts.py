from django.core.management.base import BaseCommand
from karmaworld.apps.courses.tasks import fix_note_counts

class Command(BaseCommand):
    help = """Set the field file_count on every Course and School
            to the correct value."""

    def handle(self, *args, **kwargs):
        fix_note_counts()
