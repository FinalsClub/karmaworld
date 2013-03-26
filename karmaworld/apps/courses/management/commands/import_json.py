import json
import os.path
import datetime

from django.core.management.base import BaseCommand
from django.core.files import File as DjangoFile

from karmaworld.apps.notes.models import *
# a little messy to import courses in a notes command?
from karmaworld.apps.courses.models import *

class Command(BaseCommand):
    args = 'all [clean]'
    help = """Import data to the database from .json. Expect the json in the 
        format exported by the dump_json manage command.
        The 'all' argument is required. When the 'all' argument is used, 
        import_json expects the following files:
            - schools.json
            - courses.json
            - notes.json
        If an notes object in notes.json include a 'note_file' key, assume this 
        file can be found relative to the following directory:
            files/ 

        If the optional 'clean' argument is specified, all notes, courses and 
        files will be deleted from the db before importing 

        When importing notes and courses, it is not currently possible to 
        import ForeignKey values for schools or courses that have already been 
        saved in the db. ForeignKey values within json files may only refer to 
        id values included in the current batch of .json files
    """

    def handle(self, *args, **kwargs):

        printl = self.stdout.write

        if 'all' not in args:
            printl('specify "all" - assumes schools.json, notes.json and courses.json')
            return

        if 'clean' in args:
            for n in Note.objects.all(): n.delete()
            for c in Course.objects.all(): c.delete()
            for s in School.objects.all(): s.delete()

        # read json files
        with open('schools.json', 'r') as f:
            school_dicts = json.load(f)

        with open('notes.json', 'r') as f:
            note_dicts = json.load(f)

        with open('courses.json', 'r') as f:
            course_dicts = json.load(f)

        printl('Schools found: %d\n' % len(school_dicts))
        printl('Notes found: %d\n' % len(note_dicts))
        printl('Courses found: %d\n' % len(course_dicts))

        # Store all the new School orm objects in a dictionary
        schools_by_old_id = {}
        courses_by_old_id = {}

        #Schools
        printl('Importing Schools\n')
        for school in school_dicts:
            old_id = school['id']
            del school['id']
            s = School(**school)
            s.save()
            schools_by_old_id[old_id] = s

        # Courses
        printl('Importing Courses\n')
        for course in course_dicts:
            #printl('Course: ' + course['name'] + '\n')
            course['updated_at'] = datetime.datetime.utcnow()
            course['created_at'] = datetime.datetime.utcnow()

            # remove the old ids from the dict
            old_id = course['id']
            old_school_id = course['school_id']
            del course['id']        # Have this auto generated
            del course['school_id'] # use the actual school instead

            c = Course(**course)
            c.school = schools_by_old_id[old_school_id]
            c.save()
            courses_by_old_id[old_id] = c

        # Notes
        printl('Importing Notes\n')
        for note in note_dicts:

            # These keys cannot be pased as keyword arguments
            tags = None
            if 'tags' in note:
                tags = note['tags']
                del note['tags']

            note_file = None
            if 'note_file' in note and note['note_file']:
                note_file = os.path.join('files', note['note_file']) # specify folder for files
                del note['note_file']

            # replace the string with this value
            note['uploaded_at'] = datetime.datetime.utcnow()

            old_course_id = note['course_id']
            del note['id']
            del note['course_id']

            # we need to re-generate the slug
            if 'slug' in note:
                del note['slug']

            n = Note(**note)

            n.course = courses_by_old_id[old_course_id]
            n.save()

            # Add the tags, if any
            if tags:
                for t in tags: n.tags.add(t)

            if note_file:
                printl(note_file + '\n')
                with open(note_file) as f:
                    df = DjangoFile(f)
                    _, file_name = os.path.split(note_file) # careful
                    n.note_file.save(file_name, df)

            n.save()

        for c in Course.objects.all(): c.update_note_count()
        for s in School.objects.all(): s.update_note_count()

