#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

# This file is only temporary as Note.html data gets moved onto S3.
# Once Note.html no longer exists, this function should be removed.

import hashlib
from cStringIO import StringIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from karmaworld.apps.notes.models import Note

class Command(BaseCommand):
    args = 'none'
    help = """
           Upload Note.html to the S3 system.
           """

    def handle(self, *args, **kwargs):
        for note in Note.objects.iterator():
            if note.static_html:
                # don't reprocess notes that are already on S3.
                print "Skipping {0}".format(str(note))
                continue

            filepath = note.get_relative_s3_path()
            if default_storage.exists(filepath):
                # HTML file is already uploaded if its slug is already there.
                note.static_html = True
                note.save()
                print "Marking {0} as uploaded.".format(filepath)
                continue
     
            # Copy pasta!

            # This is a pretty ugly hackified answer to some s3boto shortcomings
            # and some decent default settings chosen by django-storages.
    
            print "Processing {0}".format(filepath)
            html = note.filter_html(note.html)
            # S3 upload wants a file-like object.
            htmlflo = StringIO(html)
            # Create the new key (key == filename in S3 bucket)
            newkey = default_storage.bucket.new_key(filepath)
            # Upload data!
            newkey.send_file(htmlflo)

            # Make sure the upload went through
            if not newkey.exists():
                # oh well. log it and continue on.
                print 'Unable to find {0}'.format(str(newkey))
                continue

            # Local HTML checksum
            htmlflo.seek(0)
            htmlflo_check = hashlib.sha1(htmlflo.read()).hexdigest()

            # Remote HTML checksum
            with default_storage.open(filepath, 'r') as s3file:
                s3_check = hashlib.sha1(s3file.read()).hexdigest()

            if htmlflo_check == s3_check:
                # Mark this note as available from the static host
                note.static_html = True
                # Scrub its HTML to clean up the database.
                note.html = ''
                note.save()
                print "Completed upload of {0}".format(filepath)
            else:
                print "Checksum mismatch for {0}:\n{1}\n{2}\n".format(filepath,
                  htmlflo_check, s3_check)
