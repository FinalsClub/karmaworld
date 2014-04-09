#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import traceback
import logging

from django.core import serializers
from django.forms.formsets import formset_factory
from karmaworld.apps.courses.models import Course
from karmaworld.apps.notes.search import SearchIndex
from karmaworld.apps.quizzes.forms import KeywordForm
from karmaworld.apps.quizzes.models import Keyword
from karmaworld.apps.users.models import NoteKarmaEvent
from karmaworld.utils.ajax_utils import *

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import DetailView, ListView
from django.views.generic import FormView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from karmaworld.apps.notes.models import Note
from karmaworld.apps.notes.forms import NoteForm


logger = logging.getLogger(__name__)

THANKS_FIELD = 'thanks'
USER_PROFILE_THANKS_FIELD = 'thanked_notes'
FLAG_FIELD = 'flags'
USER_PROFILE_FLAGS_FIELD = 'flagged_notes'


class NoteDetailView(DetailView):
    """ Class-based view for the note html page """
    model = Note
    context_object_name = u"note" # name passed to template
    keyword_form_class = formset_factory(KeywordForm)

    def post(self, request, *args, **kwargs):
        formset = self.keyword_form_class(request.POST)
        if formset.is_valid():
            self.keyword_form_valid(formset)
            self.keyword_formset = self.keyword_form_class(initial=self.get_initial_keywords())
            return super(NoteDetailView, self).get(request, *args, **kwargs)
        else:
            self.keyword_formset = formset
            return super(NoteDetailView, self).get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.keyword_formset = self.keyword_form_class(initial=self.get_initial_keywords())
        return super(NoteDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Generate custom context for the page rendering a Note
            + if pdf, set the `pdf` flag
        """

        kwargs['keyword_prototype_form'] = KeywordForm
        kwargs['keyword_formset'] = self.keyword_formset

        if self.object.is_pdf():
            kwargs['pdf_controls'] = True

        if self.request.user.is_authenticated():
            try:
                self.request.user.get_profile().thanked_notes.get(pk=self.object.pk)
                kwargs['already_thanked'] = True
            except ObjectDoesNotExist:
                pass

            try:
                self.request.user.get_profile().flagged_notes.get(pk=self.object.pk)
                kwargs['already_flagged'] = True
            except ObjectDoesNotExist:
                pass

        return super(NoteDetailView, self).get_context_data(**kwargs)

    def get_initial_keywords(self):
        existing_keywords = self.get_object().keyword_set.order_by('id')
        initial_data = [{'keyword': keyword.word, 'definition': keyword.definition, 'id': keyword.pk}
                        for keyword in existing_keywords]
        return initial_data

    def keyword_form_valid(self, formset):
        for form in formset:
            word = form['keyword'].data
            definition = form['definition'].data
            id = form['id'].data
            if word == '':
                continue
            try:
                keyword_object = Keyword.objects.get(id=id)
            except (ValueError, ObjectDoesNotExist):
                keyword_object = Keyword()

            keyword_object.note = self.get_object()
            keyword_object.word = word
            keyword_object.definition = definition
            keyword_object.save()


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
        if request.POST['action'] == 'tags-form':
            view = NoteSaveView.as_view()
        else:
            view = NoteDetailView.as_view()
        return view(request, *args, **kwargs)


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
    return ajax_increment(Note, request, pk, THANKS_FIELD, USER_PROFILE_THANKS_FIELD, process_note_thank_events)


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
    return ajax_increment(Note, request, pk, FLAG_FIELD, USER_PROFILE_FLAGS_FIELD, process_note_flag_events)


def process_downloaded_note(request_user, note):
    """Record that somebody has downloaded a note"""
    if request_user.is_authenticated() and request_user != note.user:
        NoteKarmaEvent.create_event(request_user, note, NoteKarmaEvent.DOWNLOADED_NOTE)
    if request_user.is_authenticated() and note.user:
        NoteKarmaEvent.create_event(note.user, note, NoteKarmaEvent.HAD_NOTE_DOWNLOADED)


def downloaded_note(request, pk):
    """Record that somebody has flagged a note."""
    return ajax_pk_base(Note, request, pk, process_downloaded_note)


def edit_note_tags(request, pk):
    """
    Saves the posted string of tags
    """
    if request.method == "POST" and request.is_ajax() and request.user.is_authenticated() and request.user.get_profile().can_edit_items():
        note = Note.objects.get(pk=pk)
        note.tags.set(request.body)

        note_json = serializers.serialize('json', [note,])
        resp = json.loads(note_json)[0]
        resp['fields']['tags'] = list(note.tags.names())

        return HttpResponse(json.dumps(resp), mimetype="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'Invalid request'}),
                                      mimetype="application/json")

