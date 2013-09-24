#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

import datetime

from django.db import models
import django_filepicker

from karmaworld.apps.notes.models import Document
from karmaworld.apps.notes.models import Note
from karmaworld.apps.document_upload import tasks


class RawDocument(Document):
    is_processed = models.BooleanField(default=False)

    class Meta:
        """ Sort files most recent first """
        ordering = ['-uploaded_at']


    def __unicode__(self):
        return u"{0} @ {1}".format(self.ip, self.uploaded_at)

    def convert_to_note(self):
        """ polymorph this object into a note.models.Note object  """
        print "begin convert_to_note"
        note = Note(
                course=self.course,
                name=self.name,
                slug=self.slug,
                ip=self.ip,
                uploaded_at=self.uploaded_at,
                fp_file=self.fp_file)
        note.save()
        for tag in self.tags.all():
            note.tags.add(tag)
        print "finish convert_to_note"
        return note

    def save(self, *args, **kwargs):
        print "`RawDocument.save()`"
        super(RawDocument, self).save(*args, **kwargs)
        if not self.is_processed:
            print "\t document not processed yet, doing that now"
            tasks.process_raw_document.delay(self)
            print "\t this arrow should point to the word now ^"
