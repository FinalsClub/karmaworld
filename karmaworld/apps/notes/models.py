#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for the notes django app.
    Contains only the minimum for handling files and their representation
"""
import datetime
import traceback
import logging
from allauth.account.signals import user_logged_in
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import SET_NULL
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from karmaworld.apps.notes.gdrive import UPLOADED_NOTES_SESSION_KEY
import os
import urllib

from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.text import slugify
import django_filepicker
from bs4 import BeautifulSoup as BS
from taggit.managers import TaggableManager

from karmaworld.apps.courses.models import Course
from karmaworld.apps.licenses.models import License
from karmaworld.apps.notes.search import SearchIndex
from karmaworld.settings.manual_unique_together import auto_add_check_unique_together


logger = logging.getLogger(__name__)
fs = FileSystemStorage(location=settings.MEDIA_ROOT)


def _choose_upload_to(instance, filename):
    # /school/course/year/month/day
    return u"{school}/{course}/{year}/{month}/{day}".format(
        school=instance.course.school.slug,
        course=instance.course.slug,
        year=instance.uploaded_at.year,
        month=instance.uploaded_at.month,
        day=instance.uploaded_at.day)


class Document(models.Model):
    """
    An Abstract Base Class representing a document intended to be subclassed.
    """
    course          = models.ForeignKey(Course)
    tags            = TaggableManager(blank=True)
    name            = models.CharField(max_length=255, blank=True, null=True)
    slug            = models.SlugField(max_length=255, unique=True)

    # license if different from default
    license         = models.ForeignKey(License, blank=True, null=True)

    # provide an upstream file link
    upstream_link   = models.URLField(max_length=1024, blank=True, null=True, unique=True)

    # metadata relevant to the Upload process
    user            = models.ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    ip              = models.GenericIPAddressField(blank=True, null=True,
                        help_text=u"IP address of the uploader")
    uploaded_at     = models.DateTimeField(null=True, default=datetime.datetime.utcnow)


    # if True, NEVER show this file
    # WARNING: This may throw an error on migration
    is_hidden       = models.BooleanField(default=False)

    fp_file = django_filepicker.models.FPFileField(
            upload_to=_choose_upload_to,
            storage=fs,
            null=True, blank=True,
            help_text=u"An uploaded file reference from Filepicker.io")
    mimetype = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-uploaded_at']

    def _generate_unique_slug(self):
        """ generate a unique slug based on name and uploaded_at  """
        _slug = slugify(unicode(self.name))
        klass = self.__class__
        collision = klass.objects.filter(slug=_slug)
        if collision:
            _slug = u"{0}-{1}-{2}-{3}".format(
                    _slug, self.uploaded_at.month,
                    self.uploaded_at.day, self.uploaded_at.microsecond)
        self.slug = _slug

    def get_file(self):
        """ Downloads the file from filepicker.io and returns a
        Django File wrapper object """
        # clean up any old downloads that are still hanging around
        if hasattr(self, 'tempfile'):
            self.tempfile.close()
            delattr(self, 'tempfile')

        if hasattr(self, 'filename'):
            # the file might have been moved in the meantime so
            # check first
            if os.path.exists(self.filename):
                os.remove(self.filename)
            delattr(self, 'filename')

        # The temporary file will be created in a directory set by the
        # environment (TEMP_DIR, TEMP or TMP)
        self.filename, header = urllib.urlretrieve(self.fp_file.name)
        name = os.path.basename(self.filename)
        disposition = header.get('Content-Disposition')
        if disposition:
            name = disposition.rpartition("filename=")[2].strip('" ')
        filename = header.get('X-File-Name')
        if filename:
            name = filename

        self.tempfile = open(self.filename, 'r')
        return File(self.tempfile, name=name)

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self._generate_unique_slug()
        super(Document, self).save(*args, **kwargs)


class NoteManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, fp_file, upstream_link):
        """
        Return a Note defined by its Filepicker and upstream URLs.
        """
        return self.get(fp_file=fp_file,upstream_link=upstream_link)


class Note(Document):
    """ 
    A django model representing an uploaded file and associated metadata.
    """
    objects = NoteManager()

    # FIXME: refactor file choices after FP.io integration
    UNKNOWN_FILE = '???'
    FILE_TYPE_CHOICES = (
        ('doc', 'MS Word compatible file (.doc, .docx, .rtf, .odf)'),
        ('img', 'Scan or picture of notes'),
        ('pdf', 'PDF file'),
        ('ppt', 'Powerpoint'),
        ('txt', 'Text'),
        (UNKNOWN_FILE, 'Unknown file'),
    )

    file_type       = models.CharField(max_length=15,
                            choices=FILE_TYPE_CHOICES,
                            default=UNKNOWN_FILE,
                            blank=True, null=True)

    # Cache the Google drive file link
    gdrive_url      = models.URLField(max_length=1024, blank=True, null=True, unique=True)

    # Upload files to MEDIA_ROOT/notes/YEAR/MONTH/DAY, 2012/10/30/filename
    pdf_file       = models.FileField(
                            storage=fs,
                            upload_to="notes/%Y/%m/%d/",
                            blank=True, null=True)

    # Generated by Google Drive but saved locally
    text            = models.TextField(blank=True, null=True)
    static_html     = models.BooleanField(default=False)

    # html is deprecated. delete once data is all sorted.
    html            = models.TextField(blank=True, null=True)

    # Academic year of course
    year            = models.IntegerField(blank=True, null=True,\
                        default=datetime.datetime.utcnow().year)

    # Number of times this note has been flagged as abusive/spam.
    flags           = models.IntegerField(default=0,null=False)

    # Social media tracking
    tweeted         = models.BooleanField(default=False)
    thanks          = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('fp_file', 'upstream_link')
        ordering = ['-uploaded_at']

    def __unicode__(self):
        return u"Note at {0} (from {1})".format(self.fp_file, self.upstream_link)

    def natural_key(self):
        """
        A Note is uniquely defined by both the Filepicker link and the upstream
        link. The Filepicker link should be unique by itself, but it may be
        null in the database, so the upstream link component should resolve
        those cases.
        """
        # gdrive_url might also fit the bill?
        return (self.fp_file, self.upstream_link)

    def get_relative_s3_path(self):
        """
        returns s3 path relative to the appropriate bucket.
        """
        # Note.slug will be unique and brought in from RawDocument or created
        # upon save() inside RawDocument.convert_to_note(). It makes for a good
        # filename and its pretty well guaranteed to be there.
        return 'html/{0}.html'.format(self.slug)

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

    def filter_html(self, html):
        """
        Apply all sanitizing filters to HTML.
        Takes in HTML string and outputs HTML string.
        """
        # Fun fact: This could be made into a static method.
        if not html or not len(html):
            # if there was no HTML, return an empty string
            return ''

        # TODO adding from_encoding (if known) will speed up the process
        # http://www.crummy.com/software/BeautifulSoup/bs4/doc/#encodings
        soup = BS(html)
        # Iterate through filters, applying all to the soup object.
        for soupfilter in (
          self.sanitize_anchor_html,
        ):
            soup = soupfilter(soup)
        # Return BeautifulSoup cleaned up HTML in UTF-8
        # http://www.crummy.com/software/BeautifulSoup/bs4/doc/#output-encoding
        return soup.prettify()

    def sanitize_anchor_html(self, soup):
        """
        Filter the given BeautifulSoup obj by adding target=_blank to all
        anchor tags.
        Returns BeautifulSoup obj.
        """
        # Fun fact: This could be made into a static method.
        # Find all a tags in the HTML
        a_tags = soup.find_all('a')
        if not a_tags or not len(a_tags):
            # nothing to process.
            return soup

        # build a tag sanitizer
        def set_attribute_target(tag):
            tag['target'] = '_blank'
        # set all anchors to have target="_blank"
        map(set_attribute_target, a_tags)

        # return filtered soup
        return soup

    def _update_parent_updated_at(self):
        """ update the parent Course.updated_at model
            with the latest uploaded_at """
        self.course.updated_at = self.uploaded_at
        self.course.save()

    def save(self, *args, **kwargs):
        if self.uploaded_at and self.uploaded_at > self.course.updated_at:
            self._update_parent_updated_at()
        super(Note, self).save(*args, **kwargs)


auto_add_check_unique_together(Note)


def update_note_counts(note_instance):
    try:
        # test if the course still exists, or if this is a cascade delete.
        note_instance.course
    except Course.DoesNotExist:
        # this is a cascade delete. there is no course to update
        pass
    else:
        # course exists
        note_instance.course.update_note_count()
        note_instance.course.school.update_note_count()

@receiver(pre_save, sender=Note, weak=False)
def note_pre_save_receiver(sender, **kwargs):
    """Stick an instance of the pre-save value of
    the given Note instance in the instances itself.
    This will be looked at in post_save."""
    if not 'instance' in kwargs:
        return

    try:
        kwargs['instance'].old_instance = Note.objects.get(id=kwargs['instance'].id)
    except ObjectDoesNotExist:
        pass

@receiver(post_save, sender=Note, weak=False)
def note_save_receiver(sender, **kwargs):
    if not 'instance' in kwargs:
        return
    note = kwargs['instance']

    try:
        index = SearchIndex()
        if kwargs['created']:
            update_note_counts(note)
            index.add_note(note)
        else:
            index.update_note(note, note.old_instance)
    except Exception:
        logger.error("Error with IndexDen:\n" + traceback.format_exc())


@receiver(post_delete, sender=Note, weak=False)
def note_delete_receiver(sender, **kwargs):
    if not 'instance' in kwargs:
        return
    note = kwargs['instance']

    # Update course and school counts of how
    # many notes they have
    update_note_counts(kwargs['instance'])

    # Remove document from search index
    index = SearchIndex()
    index.remove_note(note)

@receiver(user_logged_in, weak=True)
def find_orphan_notes(sender, **kwargs):
    user = kwargs['user']
    s = kwargs['request'].session
    uploaded_note_ids = s.get(UPLOADED_NOTES_SESSION_KEY, [])
    notes = Note.objects.filter(id__in=uploaded_note_ids)
    for note in notes:
        note.user = user
        note.save()
