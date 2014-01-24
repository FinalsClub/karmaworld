#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import json
import traceback
import logging
from django.core.exceptions import ObjectDoesNotExist
from karmaworld.apps.courses.models import Course
from karmaworld.apps.notes.search import SearchIndex
from karmaworld.apps.users.models import NoteKarmaEvent
from karmaworld.utils.ajax_increment import *

import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.generic import DetailView, ListView
from django.views.generic import FormView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from karmaworld.apps.notes.models import Note
from karmaworld.apps.notes.forms import NoteForm


logger = logging.getLogger(__name__)

PDF_MIMETYPES = (
    'application/pdf',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
)

def is_pdf(self):
    if self.object.file_type == 'pdf':
        return True
    return False

def is_ppt(self):
    if self.object.file_type == 'ppt':
        return True
    return False

THANKS_FIELD = 'thanks'
FLAG_FIELD = 'flags'

class NoteDetailView(DetailView):
    """ Class-based view for the note html page """
    model = Note
    context_object_name = u"note" # name passed to template

    def get_context_data(self, **kwargs):
        """ Generate custom context for the page rendering a Note
            + if pdf, set the `pdf` flag
        """
        # not current using these
        #kwargs['hostname'] = Site.objects.get_current()

        kwargs['pdf'] = is_pdf(self)
        kwargs['ppt'] = is_ppt(self)

        if self.object.mimetype in PDF_MIMETYPES:
            kwargs['pdf_controls'] = True

        if self.request.session.get(format_session_increment_field(Note, self.object.id, THANKS_FIELD), False):
            kwargs['already_thanked'] = True

        if self.request.session.get(format_session_increment_field(Note, self.object.id, FLAG_FIELD), False):
            kwargs['already_flagged'] = True

        return super(NoteDetailView, self).get_context_data(**kwargs)


class NoteSaveView(FormView, SingleObjectMixin):
    """ Save a Note and then view the page, 
        behaves the same as NoteDetailView, except for saving the
        NoteForm ModelForm
    """
    form_class = NoteForm
    model = Note
    template_name = 'notes/note_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'object': self.get_object(),
        }
        print "get context for NoteSaveView"
        return super(NoteSaveView, self).get_context_data(**context)

    def get_success_url(self):
        """ On form submission success, redirect to what url """
        #TODO: redirect to note slug if possible (auto-slugify)
        return u'/{school_slug}/{course_slug}?url=/{school_slug}/{course_slug}/{pk}&name={name}&thankyou'.format(
                school_slug=self.object.course.school.slug,
                course_slug=self.object.course.slug,
                pk=self.object.pk,
                name=self.object.name
            )

    def form_valid(self, form):
        """ Actions to take if the submitted form is valid
            namely, saving the new data to the existing note object
        """
        self.object = self.get_object()
        if len(form.cleaned_data['name'].strip()) > 0:
            self.object.name = form.cleaned_data['name']
        self.object.year = form.cleaned_data['year']
        # use *arg expansion to pass tags a list of tags
        self.object.tags.add(*form.cleaned_data['tags'])
        # User has submitted this form, so set the SHOW flag
        self.object.is_hidden = False
        self.object.save()
        return super(NoteSaveView, self).form_valid(form)

    def form_invalid(self, form):
        """ Do stuff when the form is invalid !!! TODO """
        # TODO: implement def form_invalid for returning a form with input and error
        print "running form_invalid"
        print form
        print form.errors


class NoteView(View):
    """ Notes superclass that wraps http methods """

    def get(self, request, *args, **kwargs):
        view = NoteDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = NoteSaveView.as_view()
        return view(request, *args, **kwargs)


class RawNoteDetailView(DetailView):
    """ Class-based view for the raw note html for iframes """
    template_name = u'notes/note_raw.html'
    context_object_name = u"note"
    model = Note


class PDFView(DetailView):
    """ Render PDF files in an iframe based on ID"""
    template_name = u'partial/pdfembed.html'
    model = Note

    def get_context_data(self, **kwargs):
        """ Generate a path to the pdf file associated with this note
            by generating a path to the MEDIA_URL by hand """

        if is_ppt(self):
            kwargs['pdf_path'] = "{0}{1}".format(settings.MEDIA_URL,
                os.path.basename(self.object.pdf_file.name))
        elif is_pdf(self):
            kwargs['pdf_path'] = self.object.fp_file
            #kwargs['pdf_path'] = "{0}{1}".format(settings.MEDIA_URL,
            #    os.path.basename(self.object.note_file.name))

        return super(PDFView, self).get_context_data(**kwargs)


class NoteSearchView(ListView):
    template_name = 'notes/search_results.html'

    def get_queryset(self):
        if not 'query' in self.request.GET:
            return Note.objects.none()

        if 'page' in self.request.GET:
            page = int(self.request.GET['page'])
        else:
            page = 0

        try:
            index = SearchIndex()

            if 'course_id' in self.request.GET:
                raw_results = index.search(self.request.GET['query'],
                                                  self.request.GET['course_id'],
                                                  page=page)
            else:
                raw_results = index.search(self.request.GET['query'],
                                            page=page)

        except Exception:
            logger.error("Error with IndexDen:\n" + traceback.format_exc())
            self.error = True
            return Note.objects.none()
        else:
            self.error = False

        instances = Note.objects.in_bulk(raw_results.ordered_ids)
        results = []
        for id in raw_results.ordered_ids:
            if id in instances:
                results.append((instances[id], raw_results.snippet_dict[id]))
        self.has_more = raw_results.has_more

        return results

    def get_context_data(self, **kwargs):
        if 'query' in self.request.GET:
            kwargs['query'] = self.request.GET['query']

        if 'course_id' in self.request.GET:
            kwargs['course'] = Course.objects.get(id=self.request.GET['course_id'])

        if self.error:
            kwargs['error'] = True
            return super(NoteSearchView, self).get_context_data(**kwargs)

        # If query returned more search results than could
        # fit on one page, show "Next" button
        if self.has_more:
            kwargs['has_next'] = True
            if 'page' in self.request.GET:
                kwargs['next_page'] = int(self.request.GET['page']) + 1
            else:
                kwargs['next_page'] = 1

        # If the user is looking at a search result page
        # that isn't the first one, show "Prev" button
        if 'page' in self.request.GET and \
            int(self.request.GET['page']) > 0:
            kwargs['has_prev'] = True
            kwargs['prev_page'] = int(self.request.GET['page']) - 1

        return super(NoteSearchView, self).get_context_data(**kwargs)


def process_note_thank_events(request_user, note):
    # Give points to the person who uploaded this note
    if note.user != request_user and note.user:
        NoteKarmaEvent.create_event(note.user, note, NoteKarmaEvent.THANKS)


def thank_note(request, pk):
    """Record that somebody has thanked a note."""
    return ajax_increment(Note, request, pk, THANKS_FIELD, process_note_thank_events)


def process_note_flag_events(request_user, note):
    # Take a point away from person flagging this note
    if request_user.is_authenticated():
        NoteKarmaEvent.create_event(request_user, note, NoteKarmaEvent.GIVE_FLAG)
    # If this is the 6th time this note has been flagged,
    # punish the uploader
    if note.flags == 6 and note.user:
        NoteKarmaEvent.create_event(note.user, note, NoteKarmaEvent.GET_FLAGGED)


def flag_note(request, pk):
    """Record that somebody has flagged a note."""
    return ajax_increment(Note, request, pk, FLAG_FIELD, process_note_flag_events)


def process_downloaded_note(request_user, note):
    """Record that somebody has downloaded a note"""
    if request_user.is_authenticated() and request_user != note.user:
        NoteKarmaEvent.create_event(request_user, note, NoteKarmaEvent.DOWNLOADED_NOTE)
    if request_user.is_authenticated() and note.user:
        NoteKarmaEvent.create_event(note.user, note, NoteKarmaEvent.HAD_NOTE_DOWNLOADED)


def downloaded_note(request, pk):
    """Record that somebody has flagged a note."""
    return ajax_base(Note, request, pk, process_downloaded_note)


