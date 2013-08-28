#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

import datetime

from django.db import models
import django_filepicker

from karmaworld.apps.notes.models import Document

class RawDocument(Document):
    is_processed = models.BooleanField(default=False)


    class Meta:
        """ Sort files most recent first """
        ordering = ['-uploaded_at']


    def __unicode__(self):
        return u"{0} @ {1}".format(self.ip, self.uploaded_at)

    def convert_to_note(self):
        """ polymorph this object into a note.models.Note object  """
        pass
