#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for the licenses in the django app.
"""

from django.db import models

class LicenseManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, name):
        """
        Return a License defined by its brief name.
        """
        return self.get(name=name)


class License(models.Model):
    """
    Track licenses for notes which are different from the default license
    assumed for the site.
    """
    objects = LicenseManager()

    name = models.CharField(max_length=80,unique=True)
    html = models.TextField()

    def __unicode__(self):
        return u'License: {0}'.format(self.name)

    def natural_key(self):
        """
        A License is uniquely defined by its brief name.
        """
        return (self.name,)
