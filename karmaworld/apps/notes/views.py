#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from karmaworld.apps.notes.models import Note

class NoteDetailView(DetailView):
    """ Class-based view for the note html page """
    # name passed to template
    context_object_name = u"note"
    model = Note

class RawNoteDetailView(DetailView):
    """ Class-based view for the raw note html for iframes """
    template_name = u'notes/note_raw.html'
    context_object_name = u"note"
    model = Note

def raw_file(request, pk):
    """ Display the raw html from a Note object for embedding in an iframe """
    note = get_object_or_404(Note, pk=pk)
    return HttpResponse(note.html)
