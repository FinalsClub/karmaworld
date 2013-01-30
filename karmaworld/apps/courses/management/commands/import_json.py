import json
import os.path
import datetime

from django.core.management.base import BaseCommand
from django.core.files import File as DjangoFile

from karmaworld.apps.notes.models import *
# a little messy to import courses in a notes command?
from karmaworld.apps.courses.models import *

class Command(BaseCommand):

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

		#Schools
		printl('Importing Schools\n')
		for school in school_dicts:
			s = School(**school)
			s.save()

		# Courses
		printl('Importing Courses\n')
		for course in course_dicts:
			#printl('Course: ' + course['name'] + '\n')
			course['updated_at'] = datetime.datetime.utcnow()
			course['created_at'] = datetime.datetime.utcnow()

			c = Course(**course)
			c.save()

		# Notes
		printl('Importing Notes\n')
		for note in note_dicts:

			# These keys cannot be pased as keyword arguments
			tags = None
			if 'tags' in note:
				tags = note['tags']
				del note['tags']

			file_path = None
			if 'file_path' in note and note['file_path']:
				file_path = os.path.join('files', note['file_path']) # specify folder for files
				del note['file_path']

			# replace the string with this value
			note['uploaded_at'] = datetime.datetime.utcnow()

			n = Note(**note)

			# Add the tags, if any
			if tags:
				for t in tags: n.tags.add(t)

			if file_path:
				with open(file_path) as f:
					df = DjangoFile(f)
					_, file_name = os.path.split(file_path) # careful
					n.note_file.save(file_name, df)

			n.save()

		for c in Course.objects.all(): c.update_note_count()
		for s in School.objects.all(): s.update_note_count()

