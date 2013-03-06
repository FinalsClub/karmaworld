#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for the courses django app.
    Handles courses, and their related models
    Courses are the first class object, they contain notes.
    Courses have a manytoone relation to schools.
"""
import datetime

from django.db import models
from django.template import defaultfilters

class School(models.Model):
    """ A grouping that contains many courses """
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=150, null=True)
    location    = models.CharField(max_length=255, blank=True, null=True)
    url         = models.URLField(max_length=511, blank=True)
    # Facebook keeps a unique identifier for all schools
    facebook_id = models.BigIntegerField(blank=True, null=True)
    # United States Department of Education institution_id
    usde_id     = models.BigIntegerField(blank=True, null=True)
    file_count  = models.IntegerField(default=0)

    class Meta:
        """ Sort School by file_count descending, name abc=> """
        ordering = ['-file_count', 'name']


    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ Save school and generate a slug if one doesn't exist """
        if not self.slug:
            self.slug = defaultfilters.slugify(self.name)
        super(School, self).save(*args, **kwargs)

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    def update_note_count(self):
        """ Update the School.file_count by summing the 
            contained course.file_count
        """
        self.file_count = sum([course.file_count for course in self.course_set.all()])
        self.save()

    def update_related_note_count(self):
        """ Runs the update_note_count function on all related course
            objects, then generates the self.file_count
        """
        for course in self.course_set.all():
            course.update_note_count()
        self.update_note_count()


class Course(models.Model):
    """ First class object that contains many notes.Note objects """
    # Core metadata
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=150, null=True)
    school      = models.ForeignKey(School) # Should this be optional ever?
    file_count  = models.IntegerField(default=0)

    desc        = models.TextField(max_length=511, blank=True, null=True)
    url         = models.URLField(max_length=511, blank=True, null=True)
    academic_year   = models.IntegerField(blank=True, null=True, 
                        default=datetime.datetime.now().year)

    instructor_name     = models.CharField(max_length=255, blank=True, null=True)
    instructor_email    = models.EmailField(blank=True, null=True)

    # Save school name redundantly to speed filtering
    school_name     = models.CharField(max_length=255, blank=True, null=True)

    updated_at      = models.DateTimeField(default=datetime.datetime.utcnow)
    created_at      = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-file_count', 'school', 'name']

    def __unicode__(self):
        return u"{0}: {1}".format(self.name, self.school)

    def get_absolute_url(self):
        """ return url based on school slug and self slug """
        return u"/{0}/{1}".format(self.school.slug, self.slug)

    def save(self, *args, **kwargs):
        """ Save school and generate a slug if one doesn't exist """
        if self.school_name != self.school.name:
            self.school_name = self.school.name
        super(Course, self).save(*args, **kwargs) # generate a self.id
        if not self.slug:
            self.slug = defaultfilters.slugify("%s %s" % (self.name, self.id))
            super(Course, self).save(*args, **kwargs) # Save the slug

    def get_updated_at_string(self):
        """ return the formatted style for datetime strings """
        return self.updated_at.strftime("%I%p // %a %b %d %Y")

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    def update_note_count(self):
        """ Update self.file_count by summing the note_set """
        self.file_count = self.note_set.count()
        self.save()
