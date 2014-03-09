#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import html2text
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from karmaworld.apps.notes.models import Note, NoteMarkdown

class Command(BaseCommand):
    """ Command to process all notes and add add a markdown version of the file 
        into the database """
    args = 'none'
    help = "Take all notes and use their html to create a markdown version of the document"

    def handle(self, *args, **kwargs):
        """ On all calls, clean all notes with html and not text using html2text """
        notes = Note.objects.all()

        converted_notes = 0
        for note in notes:
            if note.static_html and not note.is_pdf():
                h = html2text.HTML2Text()
                h.google_doc = True
                h.escape_snob = True
                h.unicode_snob = True

                with default_storage.open(note.get_relative_s3_path(),'r') as html:
                    markdown = h.handle(html.read().decode('utf8', 'ignore'))
                    if note.has_markdown():
                        note_markdown = note.notemarkdown
                        note_markdown.markdown = markdown
                    else:
                        note_markdown = NoteMarkdown(note=note, markdown=markdown)
                    note_markdown.save()
                converted_notes += 1
                print 'Processed {n}'.format(n=note)

            """if not note.static_html:
                # no HTML to fetch
                continue
            try:
                h = html2text.HTML2Text()
                h.escape_snob = True
                h.unicode_snob = True
                h.ignore_links = True
                h.ignore_images = True
                h.ignore_emphasis = True
                # fetch data
                with default_storage.open(note.get_relative_s3_path(),'r') as \
                  html:
                    note.text = h.handle(html.read())
                note.save()
                cleaned_notes += 1
                print 'Processed {n}'.format(n=note)
            except Exception, e:
                print note
                print e
                continue"""
        print 'Processed %s notes' % converted_notes

