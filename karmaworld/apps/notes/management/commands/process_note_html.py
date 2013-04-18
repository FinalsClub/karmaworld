#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from lxml.html import fromstring, tostring

from django.core.management.base import BaseCommand
from apps.notes.models import Note

class Command(BaseCommand):
    args = 'none'
    help = "Process note.html and modify a tags to open in new window"

    def add_target(self, tag):
        tag.attrib['target'] = '_blank'

    def handle(self, *args, **kwargs):
        notes = Note.objects.filter(html__isnull=False)

        for note in notes:
            succ, data = note.sanitize_html()
            if succ:
                print "Note %s contained %s <a>s" % (note.id, data)

