#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from celery.task import task
from karmaworld.apps.notes.gdrive import convert_with_google_drive

@task
def process_document(note):
    """ Process a file with Google Drive
        populates and saves the Note.html, Note.text

        :note: A `karmaworld.apps.notes.models.Note` instance associated, document or pdf file
        :returns: True on success, else False
    """
    print "Processing document: %s -- %s" % (note.id, note.name)
    try:
        convert_with_google_drive(note)
    except Exception, e:
        print "\terror processing doc: %s -- %s" % (note.id, note.name)
        return False
    return True
