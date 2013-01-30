import json
import os.path
import datetime

from django.core.management.base import BaseCommand

from karmaworld.apps.notes.models import *
# a little messy to import courses in a notes command?
from karmaworld.apps.courses.models import *

def school_to_dict(school):
	d = {
		'id':school.id,
		'name':school.name, 
		'slug':school.slug,
		'location':school.location, 
		'url':school.url
	}

	if school.url:
		d['url'] = school.url
	if school.facebook_id:
		d['facebook_id'] = school.facebook_id
	if school.usde_id:
		d['usde_id'] = school.usde_id

	return d

def note_to_dict(note):
	d = {
		'name': note.name, 
		'course_id': note.course.id,
	    'slug': note.slug,
	    'uploaded_at': str(note.uploaded_at),
	    'id': note.id
	}

	if note.html:
		d['html'] = note.html

	if note.text:
		d['text'] = note.text

	if note.file_type and note.file_type != '???':
		d['file_type'] = note.file_type

	if note.tags.exists():
		d['tags'] = [str(tag) for tag in note.tags.all()]

	if note.desc:
		d['desc'] = note.desc

	if note.note_file:
		_, filename = os.path.split(note.note_file.name)
		if filename:
			d['note_file'] = filename

	return d

def course_to_dict(course):
	d = {
		'name': course.name,
		'slug': course.slug,
		'school_id': course.school.id,
	}

	if course.desc:
		d['desc'] = course.desc

	if course.url:
		d['url'] = course.url

	if course.instructor_name:
		d['instructor_name'] = course.instructor_name

	if course.instructor_email:
		d['instructor_email'] = course.instructor_email

	return d
	

class Command(BaseCommand):

	month = datetime.datetime.now().month
	day = datetime.datetime.now().day
	year = datetime.datetime.now().year

	date = '%02d-%02d-%04d' % (month, day, year)

	def handle(self, *args, **kwargs):

		# Schools
		schools = [school_to_dict(school) for school in School.objects.all()]
		fn = 'schools_' + self.date + '.json'
		with open(fn, 'w') as f:
			json.dump(schools, f)

		# Notes
		notes = [note_to_dict(note) for note in Note.objects.all()]
		fn = 'notes_' + self.date + '.json'
		with open(fn, 'w') as f:
			json.dump(notes, f)

		# Courses
		courses = [course_to_dict(course) for course in Course.objects.all()]
		fn = 'courses_' + self.date + '.json'
		with open(fn, 'w') as f:
			json.dump(notes, f)

