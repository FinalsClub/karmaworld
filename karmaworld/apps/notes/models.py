#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for the notes django app.
    Contains only the minimum for handling files and their representation
"""
import datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.template import defaultfilters
from taggit.managers import TaggableManager
from oauth2client.client import Credentials

from karmaworld.apps.courses.models import Course

try:
    from secrets.drive import GOOGLE_USER
except:
    GOOGLE_USER = u'admin@karmanotes.org'

fs = FileSystemStorage(location=settings.MEDIA_ROOT)

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
    tags            = TaggableManager(blank=True)

    name            = models.CharField(max_length=255, blank=True, null=True)
    slug            = models.SlugField(max_length=255, null=True)
    year            = models.IntegerField(blank=True, null=True, 
                        default=datetime.datetime.utcnow().year)
    desc            = models.TextField(max_length=511, blank=True, null=True)
    uploaded_at     = models.DateTimeField(null=True, default=datetime.datetime.utcnow)

    file_type       = models.CharField(max_length=15,
                            choices=FILE_TYPE_CHOICES,
                            default=UNKNOWN_FILE,
                            blank=True, null=True)

    # Upload files to MEDIA_ROOT/notes/YEAR/MONTH/DAY, 2012/10/30/filename
    note_file       = models.FileField(
                            storage=fs,
                            upload_to="notes/%Y/%m/%j/",
                            blank=True, null=True)

    ## post gdrive conversion data
    embed_url       = models.URLField(max_length=1024, blank=True, null=True)
    download_url    = models.URLField(max_length=1024, blank=True, null=True)
    # for word processor documents
    html            = models.TextField(blank=True, null=True)
    text            = models.TextField(blank=True, null=True)


    class Meta:
        """ Sort files by most recent first """
        ordering = ['-uploaded_at']


    def __unicode__(self):
        return u"{0}: {1} -- {2}".format(self.file_type, self.name, self.uploaded_at)

    def save(self, *args, **kwargs):
        """ override built-in save to ensure contextual self.name """
        # TODO: If self.name isn't set, generate one based on uploaded_name
        # if we fail to set the Note.name earlier than this, use the saved filename

        if not self.slug and self.name:
            # only generate a slug if the name has been set, and slug hasn't
            self.slug = defaultfilters.slugify(self.name)

        # Check if Note.uploaded_at is after Course.updated_at
        if self.uploaded_at and self.uploaded_at > self.course.updated_at:
            self.course.updated_at = self.uploaded_at
            # if it is, update Course.updated_at
            self.course.save()

        super(Note, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """ Resolve note url, use 'note' route and slug if slug
            otherwise use note.id
        """
        if self.slug is not None:
            # return a url ending in slug
            return u"/{0}/{1}/{2}".format(self.course.school.slug, self.course.slug, self.slug)
        else:
            # return a url ending in id
            return u"/{0}/{1}/{2}".format(self.course.school.slug, self.course.slug, self.id)


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
