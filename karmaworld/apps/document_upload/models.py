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
        # TODO move this to Note. superclasses should not care about subclasses,
        # but subclasses should care about parents.

        # Note inherits all fields of Document as does RawDocument.
        # Dynamically refer to all fields of RawDocument found within Document
        # and also Note.
        initdict = {}
        for field in Document._meta.get_all_field_names():
            if field in ('tags',):
                # TaggableManager does not play well with init()
                continue
            initdict[field] = getattr(self,field)
        # Create a new Note using all fields from the Document
        note = Note(**initdict)
        note.save()
        for tag in self.tags.all():
            note.tags.add(tag)
        return note

    def save(self, *args, **kwargs):
        super(RawDocument, self).save(*args, **kwargs)
        if not self.is_processed:
            tasks.process_raw_document.delay(self)
