#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import html2text
from django.core.management.base import BaseCommand
from karmaworld.apps.notes.models import Note

class Command(BaseCommand):
    """ Command to process notes with html, and without text
        to refill text sans html tags """
    args = 'none'
    help = "Take all notes with the .html property and use that to fill Note.text by stripping html"

    def handle(self, *args, **kwargs):
        """ On all calls, clean all notes with html and not text using html2text """
        notes = Note.objects.filter(html__isnull=False).filter(text__isnull=True)
        cleaned_notes = 0
        for note in notes:
            try:
                h = html2text.HTML2Text()
                h.escape_snob = True
                h.unicode_snob = True
                h.ignore_links = True
                h.ignore_images = True
                h.ignore_emphasis = True
                note.text = h.handle(note.html)
                note.save()
                cleaned_notes += 1
                print 'Processed {n}'.format(n=note)
            except Exception, e:
                print note
                print e
                continue
        print 'Processed %s notes' % cleaned_notes

