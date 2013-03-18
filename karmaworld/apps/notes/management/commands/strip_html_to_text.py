#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from lxml.html import fromstring

from django.core.management.base import BaseCommand
from apps.notes.models import Note

class Command(BaseCommand):
    args = 'none'
    help = "Take all notes with the .html property and use that to fill Note.text by stripping html"

    def handle(self, *args, **kwargs):
        notes = Note.objects.filter(html__isnull=False).filter(text__isnull=True)
        cleaned_notes = 0
        for note in notes:
            note.text = fromstring(note.html).text_content()
            note.save()
            cleaned_notes += 1
        self.stdout.write('Processed %s notes' % cleaned_notes)

