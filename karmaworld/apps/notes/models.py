#!/usr/bin/python2.7
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for the notes django app.
    Contains only the minimum for handling files and their representation
"""
import datetime

from django.db import models
from taggit.managers import TaggableManager
from oauth2client.client import Credentials

from karmaworld.apps.courses.models import Course

class Note(models.Model):
    """ A django model representing an uploaded file and associated metadata.
    """
    UNKNOWN_FILE = '???'
    FILE_TYPE_CHOICES = (
        ('doc', 'MS Word compatible file (.doc, .docx, .rtf, .odf)'),
        ('img', 'Scan or picture of notes'),
        ('pdf', 'PDF file'),
        (UNKNOWN_FILE, 'Unknown file'),
    )

    course          = models.ForeignKey(Course)
    # Tagging system
    tags            = TaggableManager()

    name            = models.CharField(max_length=255, blank=True, null=True)
    desc            = models.TextField(max_length=511, blank=True, null=True)
    uploaded_at     = models.DateTimeField(null=True, default=datetime.datetime.utcnow)

    file_type   = models.CharField(max_length=15, blank=True, null=True, choices=FILE_TYPE_CHOICES, default=UNKNOWN_FILE)
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

    def save(self, *args, **kwargs):
        """ override built-in save to ensure contextual self.name """
        # TODO: If self.name isn't set, generate one based on uploaded_name
        # if we fail to set the Note.name earlier than this, use the saved filename

        # resume save
        super(Note, self).save(*args, **kwargs)


# FIXME: replace the following GOOGLE_USER in a settings.py
GOOGLE_USER = 'seth.woodworth@gmail.com'

class DriveAuth(models.Model):
    """ stored google drive authentication and refresh token
        used for interacting with google drive """

    email = models.EmailField(default=GOOGLE_USER)
    credentials = models.TextField() # JSON of Oauth2Credential object
    stored_at = models.DateTimeField(auto_now=True)


    @staticmethod
    def get(email=GOOGLE_USER):
        """ Staticmethod for getting the singleton DriveAuth object """
        # FIXME: this is untested
        return DriveAuth.objects.filter(email=email).reverse()[0]


    def store(self, creds):
        """ Transform an existing credentials object to a db serialized """
        self.email = creds.id_token['email']
        self.credentials = creds.to_json()
        self.save()


    def transform_to_cred(self):
        """ take stored credentials and produce a Credentials object """
        return Credentials.new_from_json(self.credentials)


    def __unicode__(self):
        return u'Gdrive auth for %s created/updated at %s' % \
                    (self.email, self.stored_at)
