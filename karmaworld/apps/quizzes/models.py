#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
import datetime
from django.db import models


class Keyword(models.Model):
    word = models.CharField(max_length=1024)
    definition = models.CharField(max_length=2048, blank=True, null=True)
    note = models.ForeignKey('notes.Note', blank=True, null=True)
    ranges = models.CharField(max_length=1024, blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    unreviewed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('word', 'note', 'ranges')

    def __unicode__(self):
        return u"{w}: {d}".format(w=self.word, d=self.definition)


class HIT(models.Model):
    HITId = models.CharField(max_length=100, unique=True, null=False)
    note = models.ForeignKey(to='notes.Note', null=False)
    processed = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{i}: {p}'.format(i=self.HITId, p='processed' if self.processed else 'unprocessed')
