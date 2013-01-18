#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
"""Before running add the downloaded docs to this folder:
bin/import_json/downloaded_notes/

Run from the django shell with:
import bin.import_json.run
"""

import json
import os
import shutil
import datetime
import taggit

from os.path import join, exists, split, isdir

from django.core.files import File as DjangoFile
from django.template.defaultfilters import slugify

from apps.courses.models import *
from apps.notes.models import *


# read json files
with open('bin/import_json/schools.json', 'r') as f:
	school_dicts = json.load(f)

with open('bin/import_json/notes.json', 'r') as f:
	note_dicts = json.load(f)

with open('bin/import_json/courses.json', 'r') as f:
	course_dicts = json.load(f)

print 'Schools found:', len(school_dicts)
print 'Notes found:', len(note_dicts)	
print 'Courses found:', len(course_dicts)


def fix_file_path(note_dict):
	"""
	The old file path was an absolute path on the server:
	/var/www/uploads/filename.txt

	Look for those files in this folder:
	bin/import_json/downloaded_notes

	update the note_dictionary's file_path key with the new spec
	"""
	path, name = split(note_dict['file_path'])

	# If we have the file, copy it to the new location
	new_filename = join('bin/import_json/downloaded_notes', name)

	if exists(new_filename) and name:
		note_dict['file_path'] = new_filename

for note in note_dicts:
	fix_file_path(note)


# Import from json 
print 'updating %i schools' % len(school_dicts)
for school in school_dicts:
	s = School(**school)
	s.save()

print 'updating %i courses' % len(course_dicts)
for course in course_dicts:
	course['updated_at'] = datetime.datetime.utcnow()
	course['created_at'] = datetime.datetime.utcnow()

	# Somc courses have no school_id using arbitrary one for these
	if not course['school_id']: 
		print 'Using arbitrary school_id for course id:', course['id'], '-', course['name']
		course['school_id'] = School.objects.all()[0].id

	c = Course(**course)
	c.save()


# Import the Notes
print 'updating %i notes' % len(note_dicts)
for note in note_dicts:

	if not note['course_id']:
		print 'using arbitrary course id for note_id:', note['id'], '-', note['name']
		note['course_id'] = Course.objects.all()[0].id

	if 'slug' not in note:
		path, fn = split(note['file_path'])
		note['slug'] = slugify(fn)

	course = Course.objects.get(id=note['course_id'])
	if Note.objects.filter(slug=note['slug']).filter(course__slug=course.slug).exists():
		print 'note_slug and course slug not unique together. skipping note with id:', note['id'], '-', note['name']
		continue

	# These keys cannot be pased as keyword arguments
	tags = note['tags']
	del note['tags']
	file_path = note['file_path'] 
	del note['file_path']

	# replace the string with this value
	note['uploaded_at'] = datetime.datetime.utcnow()

	try:
		n = Note(**note)

		# Add the tags, if any
		for t in tags: n.tags.add(t)

		# double check if the file exists before trying to open file
		if exists(file_path):
			with open(file_path) as f:
				df = DjangoFile(f)
				dir, filename = split(file_path)
				print 'copying file', note['id'], ' - ', filename
				n.note_file.save(join('imported', filename), df)

		n.save()

	except (TypeError, ) as error:
		print '\nError found in note:', error
		print note['name']

