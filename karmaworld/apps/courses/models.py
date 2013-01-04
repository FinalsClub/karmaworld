#!/usr/bin/python2.7
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
    slug        = models.SlugField(null=True)
    location    = models.CharField(max_length=255, blank=True, null=True)
    url         = models.URLField(max_length=511, blank=True)
    # Facebook keeps a unique identifier for all schools
    facebook_id = models.BigIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        """ Not implemented yet """
        pass

    def save(self, *args, **kwargs):
        """ Save school and generate a slug if one doesn't exist """
        if not self.slug:
            self.slug = defaultfilters.slugify(self.name)
        super(School, self).save(*args, **kwargs)


class Course(models.Model):
    """ First class object that contains many notes.Note objects """
    # Core metadata
    name        = models.CharField(max_length=255)
    desc        = models.TextField(max_length=511, blank=True, null=True)
    slug        = models.SlugField(null=True)
    url         = models.URLField(max_length=511, blank=True, null=True)

    school      = models.ForeignKey(School) # Should this be optional ever?

    academic_year   = models.IntegerField(blank=True, null=True, 
                        default=datetime.datetime.now().year)
    instructor_name = models.CharField(max_length=255, blank=True, null=True)
    instructor_email = models.EmailField(blank=True, null=True)
    updated_at    = models.DateTimeField(default=datetime.datetime.utcnow)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{0}: {1}".format(self.name, self.school)

    @models.permalink
    def get_absolute_url(self):
        """ Not implemented yet """
        pass

    def save(self, *args, **kwargs):
        """ Save school and generate a slug if one doesn't exist """
        if not self.slug:
            self.slug = defaultfilters.slugify(self.name)
        super(Course, self).save(*args, **kwargs)
