#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

from django.db import models

class KarmaUser(models.Model):
    email = models.EmailField(blank=False, null=False, unique=True)

    def __unicode__(self):
        return u'{e}'.format(e=self.email)
