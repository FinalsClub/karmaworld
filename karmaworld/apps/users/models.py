#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
from django.contrib import admin

from django.db import models


class KarmaUserManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, email):
        """
        Return a KarmaUser defined by his/her email address.
        """
        return self.get(email=email)


class KarmaUser(models.Model):
    objects = KarmaUserManager()

    email   = models.EmailField(blank=False, null=False, unique=True)

    def __unicode__(self):
        return u'KarmaUser: {0}'.format(self.email)

    def natural_key(self):
        """
        A KarmaUser is uniquely defined by his/her email address.
        """
        return (self.email,)
