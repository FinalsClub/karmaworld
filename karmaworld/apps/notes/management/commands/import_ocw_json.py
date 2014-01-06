#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import json
import os.path
import requests

from apps.notes.models import Note
from apps.notes.gdrive import convert_raw_document
from apps.courses.models import Course
from apps.courses.models import School
from apps.courses.models import Department
from apps.licenses.models import License
from apps.document_upload.models import RawDocument
from django.core.management.base import BaseCommand
from karmaworld.secret.filepicker import FILEPICKER_API_KEY

class Command(BaseCommand):
    args = 'directory containing json files from mit-ocw-scraper'
    help = """
           This command will systematically parse all *.json files in the given
           directory and load them into the database as course notes, uploaded
           through Filepicker.

           It is assumed the json files are generated by (or follow the same
           format as) mit-ocw-scraper:
           https://github.com/AndrewMagliozzi/mit-ocw-scraper
           """

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise ArgumentError("Expected one argument, got none: please specify a directory to parse.")

        # Convert given path to an absolute path, not relative.
        path = os.path.abspath(args[0])

        if not os.path.isdir(path):
            raise ArgumentError("First argument should be a directory to parse.")

        # for now, assume the school is MIT and find by its US DepEd ID.
        # TODO for later, do something more clever
        dbschool = School.objects.filter(usde_id=121415)[0]

        # for now, assume license is the default OCW license: CC-BY-NC 3
        # TODO for later, do something more clever.
        dblicense = License.objects.filter(name='cc-by-nc-3.0')[0]

        # build Filepicker upload URL
        # http://stackoverflow.com/questions/14115280/store-files-to-filepicker-io-from-the-command-line
        fpurl = 'https://www.filepicker.io/api/store/S3?key={0}'.format(FILEPICKER_API_KEY)

        # find all *.json files in the given directory
        def is_json_file(filename):
            return filename[-5:].lower() == '.json'
        json_files = filter(is_json_file, os.listdir(path))
        # prepend filenames with absolute paths
        def full_path_to_file(filename):
            return os.path.sep.join((path, filename))
        json_files = map(full_path_to_file, json_files)

        # parse each json file and process it for courses and notes.
        for filename in json_files:
            with open(filename, 'r') as jsondata:
                # parse JSON into python
                parsed = json.load(jsondata)

                # find the department or create one.
                dept_info = {
                    'name': parsed['subject'],
                    'school': dbschool,
                    'url': parsed['departmentLink'],
                }
                dbdept = Department.objects.get_or_create(**dept_info)[0]

                # process courses
                for course in parsed['courses']:
                    # Extract the course info
                    course_info = {
                      'name': course['courseTitle'],
                      'instructor_name': course['professor'],
                      'school': dbschool,
                    }
                    # Create or Find the Course object.
                    dbcourse = Course.objects.get_or_create(**course_info)[0]
                    dbcourse.department = dbdept;
                    dbcourse.save()
                    print "Course is in the database: {0}".format(dbcourse.name)

                    if 'noteLinks' not in course:
                        print "No Notes in course."
                        continue

                    # process notes for each course
                    for note in course['noteLinks']:
                        # Check to see if the Note is already uploaded.
                        if len(Note.objects.filter(upstream_link=note['link'])):
                            print "Already there, moving on: {0}".format(note['link'])
                            continue

                        # Upload URL of note to Filepicker if it is not already
                        # in RawDocument.
                        rd_test = RawDocument.objects.filter(upstream_link=note['link'])
                        if not len(rd_test):
                            # https://developers.inkfilepicker.com/docs/web/#inkblob-store
                            print "Uploading link {0} to FP.".format(note['link'])
                            ulresp = requests.post(fpurl, data={
                              'url': note['link'],
                            })
                            ulresp.raise_for_status()
                            # Filepicker returns JSON, so use that
                            uljson = ulresp.json()

                            print "Saving raw document to database."
                            # Extract the note info
                            dbnote = RawDocument()
                            dbnote.course = dbcourse
                            dbnote.name = note['fileName']
                            dbnote.license = dblicense
                            dbnote.upstream_link = note['link']
                            dbnote.fp_file = uljson['url']
                            dbnote.mimetype = uljson['type']
                            dbnote.is_processed = True # hack to bypass celery
                            # Create the RawDocument object.
                            dbnote.save()
                        else:
                            # Find the right RawDocument
                            print "Already uploaded link {0} to FP.".format(note['link'])
                            dbnote = rd_test[0]

                        # Do tags separately
                        dbnote.tags.add('mit-ocw','karma')

                        print "Sending to GDrive and saving note to database."
                        convert_raw_document(dbnote)
                        print "This note is done."


                    print "Notes for {0} are done.".format(dbcourse.name)
