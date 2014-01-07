#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for schools.
    Handles schools and departments.
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
    priority    = models.BooleanField(default=0)
    alias       = models.CharField(max_length=255, null=True, blank=True)
    hashtag     = models.CharField(max_length=16, null=True, blank=True, unique=True, help_text='School abbreviation without #')

    class Meta:
        """ Sort School by file_count descending, name abc=> """
        ordering = ['-file_count','-priority', 'name']


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


class Department(models.Model):
    """ Department within a School. """
    name        = models.CharField(max_length=255)
    school      = models.ForeignKey(School) # Should this be optional ever?
    slug        = models.SlugField(max_length=150, null=True)
    url         = models.URLField(max_length=511, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ Save department and generate a slug if one doesn't exist """
        if not self.slug:
            self.slug = defaultfilters.slugify(self.name)
        super(Department, self).save(*args, **kwargs)
