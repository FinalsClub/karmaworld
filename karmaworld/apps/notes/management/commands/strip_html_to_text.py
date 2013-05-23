#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from lxml.html import fromstring

from django.core.management.base import BaseCommand
from apps.notes.models import Note

class Command(BaseCommand):
    """ Command to process notes with html, and without text
        to refill text sans html tags """
    args = 'none'
    help = "Take all notes with the .html property and use that to fill Note.text by stripping html"

    def handle(self, *args, **kwargs):
        """ On all calls, clean all notes with html and not text using lxml """
        notes = Note.objects.filter(html__isnull=False).filter(text__isnull=True)
        cleaned_notes = 0
        for note in notes:
            #TODO: find style tags and drop them and their contents first
            note.text = fromstring(note.html).text_content()
            note.save()
            cleaned_notes += 1
        self.stdout.write('Processed %s notes' % cleaned_notes)

