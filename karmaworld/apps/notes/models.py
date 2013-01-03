#!/usr/bin/python2.7
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for the notes django app.
    Contains only the minimum for handling files and their representation
"""
import datetime
import os

from django.db import models
from taggit.managers import TaggableManager

class Note(models.Model):
    """ A django model representing an uploaded file and associated metadata.
    """
    FILE_TYPE_CHOICES = (
        ('doc', 'MS Word compatible file (.doc, .docx, .rtf, .odf)'),
        ('img', 'Scan or picture of notes'),
        ('pdf', 'PDF file'),
        ('???', 'Unknown file'),
    )

    # Tagging system
    tags            = TaggableManager()

    name            = models.CharField(max_length=255, blank=True, null=True)
    desc            = models.TextField(max_length=511, blank=True, null=True)
    uploaded_at     = models.DateTimeField(null=True, default=datetime.datetime.utcnow)

    file_type   = models.CharField(max_length=15, blank=True, null=True, choices=FILE_TYPE_CHOICES, default='???')
    # Upload files to MEDIA_ROOT/notes/YEAR/MONTH/DAY, 2012/10/30/filename
    note_file   = models.FileField(upload_to="notes/%Y/%m/%j/", blank=True, null=True)

    ## post gdrive conversion data
    embed_url   = models.URLField(max_length=1024, blank=True, null=True)
    download_url = models.URLField(max_length=1024, blank=True, null=True)
    # for word processor documents
    html        = models.TextField(blank=True, null=True)
    text        = models.TextField(blank=True, null=True)

    # FIXME: Not Implemented
    #uploader    = models.ForeignKey(User, blank=True, null=True, related_name='notes')
    #course      = models.ForeignKey(Course, blank=True, null=True, related_name="files")
    #school      = models.ForeignKey(School, blank=True, null=True)

    def __unicode__(self):
        return u"{0}: {1} -- {2}".format(self.file_type, self.name, self.uploaded_at)
