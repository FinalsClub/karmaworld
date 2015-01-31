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
from karmaworld.apps.notes import sanitizer

class Command(BaseCommand):
    args = 'none'
    help = """
           Upload Note.html to the S3 system.
           """

    def handle(self, *args, **kwargs):
        for note in Note.objects.iterator():
            if note.static_html:
                # don't reprocess notes that are already on S3.
                print "Skipping pre-uploaded {0}".format(str(note))
                continue

            # grab the html from inside the note and process it
            html = sanitizer.sanitize_html(note.html, note.get_canonical_url())
            html = sanitizer.sanitizer.set_canonical_rel(note.get_canonical_url())
            # push clean HTML to S3
            note.send_to_s3(html)
