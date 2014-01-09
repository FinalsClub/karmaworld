import json
import math
import inspect
import os.path
import datetime

from taggit.managers import TaggableManager
from django.db import models
from django.core import serializers
from django.core.management.base import BaseCommand

import karmaworld.apps

def introspect_models(app_base):
    # Given a base app module (e.g. karmaworld.apps), introspect for models and
    # return a list of them.
    model_list = set()
    for _, app in inspect.getmembers(app_base, inspect.ismodule):
        # check for models modules
        if not hasattr(app, 'models'):
            continue
        print "Found app models module in {0}".format(app.__name__)
        # parse attributes
        for _, attr in inspect.getmembers(app.models, inspect.isclass):
            # look for Django Models
            if issubclass(attr, models.Model):
                if attr._meta.abstract:
                    print "Skipping abstract class {0}.".format(attr.__name__)
                    continue
                if attr not in model_list:
                    print "Found DB model {0}".format(attr.__name__)
                    model_list.add(attr)
                else:
                    print "Found DB model {0} again".format(attr.__name__)
    return model_list
    

def model_to_dict(model):
    # Use model introspection to extract data fields into a dictionary.
    modeldict = {}
    for field in model._meta.get_all_field_names():
        dbfield = model._meta.get_field(field)
        if type(dbfield) == models.fields.AutoField:
            # Skip auto-incrementing id data
            continue
        elif type(dbfield) == models.fields.related.ForeignKey:
            # Dump foreign key values, not Django FK objects.
            fk = getattr(model, field)
            # Find the foreign key's primary key column.
            fkpk = fk._meta.pk.name
            # get_attname() returns the DB column name.
            # extract primary key value from the related foreign key.
            modeldict[dbfield.get_attname()] = getattr(fk, fkpk)
        else:
            modeldict[field] = getattr(model,field)
    return modeldict


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
		'id': course.id
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

	help = 'Dump the database to three json files. The json format is expected by the import_json management command.'
	month = datetime.datetime.now().month
	day = datetime.datetime.now().day
	year = datetime.datetime.now().year

	date = '%02d-%02d-%04d' % (month, day, year)

	def handle(self, *args, **kwargs):

                json_eng = serializers.get_serializer('json')()
                with open('testout.json', 'w') as outfile:
                    outfile.write('')
                for model in introspect_models(karmaworld.apps):
                    print "Processing objects in {0}".format(model.__name__)
                    # parse through pages of about 50 models at a time
                    #tot = model.objects.count()
                    #pagesize = 50
                    #for i in range(0,tot,pagesize):
                    #    objs = model.objects.filter()[i:(i+pagesize)]
                    #    for obj in objs:
                    #print str(model_to_dict(model.objects.filter()[0]))
                    import sys
                    with open('testout.json', 'a') as outfile:
                        json_eng.serialize(model.objects.filter()[0:1], stream=outfile, use_natural_keys=True)
                        outfile.write('\n\n');
                    
                return

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
			json.dump(courses, f)

