#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for the licenses in the django app.
"""

from django.db import models

class License(models.Model):
    """
    Track licenses for notes which are different from the default license
    assumed for the site.
    """

    name = models.CharField(max_length=80)
    html = models.TextField()

    def __unicode__(self):
        return u'License: {0}'.format(self.name)
