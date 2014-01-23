#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

import datetime

from django.db import models
import django_filepicker

from karmaworld.apps.notes.models import Document
from karmaworld.apps.notes.models import Note
from karmaworld.apps.document_upload import tasks
from karmaworld.settings.manual_unique_together import auto_add_check_unique_together


class RawDocumentManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, fp_file, upstream_link):
        """
        Return a RawDocument defined by its Filepicker and upstream URLs.
        """
        return self.get(fp_file=fp_file,upstream_link=upstream_link)


class RawDocument(Document):
    objects      = RawDocumentManager()

    is_processed = models.BooleanField(default=False)

    class Meta:
        """ Sort files most recent first """
        ordering = ['-uploaded_at']
        unique_together = ('fp_file', 'upstream_link')

    def __unicode__(self):
        return u"RawDocument at {0} (from {1})".format(self.fp_file, self.upstream_link)

    def natural_key(self):
        """
        A RawDocument is uniquely defined by both the Filepicker link and the
        upstream link. The Filepicker link should be unique by itself, but
        it may be null in the database, so the upstream link component should
        resolve those cases.
        """
        return (self.fp_file, self.upstream_link)

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

    def save(self, user=None, *args, **kwargs):
        super(RawDocument, self).save(*args, **kwargs)
        if not self.is_processed:
            tasks.process_raw_document.delay(self, user)


auto_add_check_unique_together(RawDocument)
