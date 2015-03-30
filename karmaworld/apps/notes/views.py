#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import json
import logging
import traceback

from django.contrib import messages

from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import formset_factory

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic import UpdateView, FormView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from karmaworld.apps.notes.forms import NoteForm
from karmaworld.apps.notes.forms import NoteDeleteForm
from karmaworld.apps.notes.models import Note
from karmaworld.apps.notes.models import NoteMarkdown
from karmaworld.apps.notes.models import KEYWORD_MTURK_THRESHOLD
from karmaworld.apps.notes.search import SearchIndex
from karmaworld.apps.users.models import NoteKarmaEvent
from karmaworld.apps.courses.forms import CourseForm
from karmaworld.apps.quizzes.forms import KeywordForm
from karmaworld.apps.quizzes.tasks import submit_extract_keywords_hit
from karmaworld.apps.quizzes.tasks import get_extract_keywords_results
from karmaworld.apps.courses.models import Course
from karmaworld.apps.quizzes.models import Keyword
from karmaworld.apps.quizzes.create_quiz import quiz_from_keywords

from karmaworld.utils.ajax_utils import ajax_pk_base
from karmaworld.utils.ajax_utils import ajax_increment


logger = logging.getLogger(__name__)

THANKS_FIELD = 'thanks'
USER_PROFILE_THANKS_FIELD = 'thanked_notes'
FLAG_FIELD = 'flags'
USER_PROFILE_FLAGS_FIELD = 'flagged_notes'

def note_page_context_helper(note, request, context):

    if request.method == 'POST':
        if not note.allows_edit_by(request.user):
            # This user is Balrog. It. Shall. Not. Pass.
            return HttpResponseForbidden()
        # Only save tags if not forbidden above.
        context['note_edit_form'] = NoteForm(request.POST)
    else:
        tags_string = ','.join([str(tag) for tag in note.tags.all()])
        initial = {"name": note.name, "tags": tags_string}
        try:
            initial["html"] = note.notemarkdown.html
        except NoteMarkdown.DoesNotExist:
            pass
        context['note_edit_form'] = NoteForm(initial=initial)

    context['note_delete_form'] = NoteDeleteForm(initial={'note': note.id})

    if note.is_pdf():
        context['pdf_controls'] = True

    if request.user.is_authenticated():
        try:
            request.user.get_profile().thanked_notes.get(pk=note.pk)
            context['already_thanked'] = True
        except ObjectDoesNotExist:
            pass

        try:
            request.user.get_profile().flagged_notes.get(pk=note.pk)
            context['already_flagged'] = True
        except ObjectDoesNotExist:
            pass

class NoteView(UpdateView):
    form_class = NoteForm
    model = Note
    context_object_name = "note"
    template_name = "notes/note_base.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        self.note = self.object
        # Ensure that the requesting user has permission to edit.
        if self.note.allows_edit_by(self.request.user):
            return super(NoteView, self).form_valid(form)
        else:
            messages.error(self.request, 'Permission denied.')
            return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(NoteView, self).get_context_data(**kwargs)
        context['show_note_container'] = True
        context['pdf_controls'] = self.object.is_pdf()
        u = self.request.user
        context['already_thanked'] = (
            u.is_authenticated() and 
            u.get_profile().thanked_notes.filter(pk=self.object.pk).exists()
        )
        context['already_flagged'] = (
            u.is_authenticated() and
            u.get_profile().flagged_notes.filter(pk=self.object.pk).exists()
        )
        context['note_delete_form'] = NoteDeleteForm(initial={'note': self.object.id})
        context['note_edit_form'] = context.get('form')
        return context

    def get_initial(self, **kwargs):
        initial = super(NoteView, self).get_initial()
        try:
            initial["html"] = self.object.notemarkdown.html
        except NoteMarkdown.DoesNotExist:
            pass
        initial["tags"] = ",".join([unicode(tag) for tag in self.object.tags.all()])
        return initial


class NoteDeleteView(FormView):
    form_class = NoteDeleteForm

    def form_valid(self, form):
        self.note = Note.objects.get(id=form.cleaned_data['note'])
        # Ensure that the requesting user has permission to delete.
        if self.note.allows_delete_by(self.request.user):
            self.note.is_hidden = True
            self.note.save()
            messages.success(self.request, 'The note "{0}" was deleted successfully.'.format(self.note.name))
        else:
            messages.error(self.request, 'Permission denied.')

        return super(FormView, self).form_valid(form)

    def get_success_url(self):
        return self.note.course.get_absolute_url()


class NoteKeywordsView(FormView, SingleObjectMixin):
    """ Class-based view for the note html page """
    model = Note
    context_object_name = u"note" # name passed to template
    form_class = formset_factory(KeywordForm)
    template_name = 'notes/note_base.html'

    def get_object(self, queryset=None):
        return Note.objects.get(slug=self.kwargs['slug'])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.request.user.is_authenticated():
            raise ValidationError("Only authenticated users may set keywords.")

        formset = self.form_class(request.POST)
        if formset.is_valid():
            self.keyword_form_valid(formset)
            self.keyword_formset = self.form_class(initial=self.get_initial_keywords())
            return super(NoteKeywordsView, self).get(request, *args, **kwargs)
        else:
            self.keyword_formset = formset
            return super(NoteKeywordsView, self).get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.keyword_formset = self.form_class(initial=self.get_initial_keywords())
        return super(NoteKeywordsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['keyword_prototype_form'] = KeywordForm
        kwargs['keyword_formset'] = self.keyword_formset
        kwargs['keywords'] = Keyword.objects.filter(note=self.get_object())
        kwargs['show_keywords'] = True

        ret = note_page_context_helper(self.get_object(), self.request, kwargs)
        # check for errors returned by the helper.
        if ret:
            return ret

        return super(NoteKeywordsView, self).get_context_data(**kwargs)

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
            # If the user has deleted an existing keyword
            if not word and not definition and id:
                try:
                    keyword_object = Keyword.objects.get(id=id)
                    keyword_object.delete()
                except (ValueError, ObjectDoesNotExist):
                    pass

            # otherwise get or create a keyword
            elif word or definition:
                try:
                    keyword_object = Keyword.objects.get(id=id)
                except (ValueError, ObjectDoesNotExist):
                    keyword_object = Keyword()
                    NoteKarmaEvent.create_event(self.request.user, self.get_object(), NoteKarmaEvent.CREATED_KEYWORD)

                keyword_object.note = self.get_object()
                keyword_object.word = word
                keyword_object.definition = definition
                keyword_object.unreviewed = False
                keyword_object.save()


class NoteQuizView(TemplateView):
    template_name = 'notes/note_base.html'

    def get_context_data(self, **kwargs):
        note = Note.objects.get(slug=self.kwargs['slug'])

        ret = note_page_context_helper(note, self.request, kwargs)
        # check for errors returned by the helper.
        if ret:
            return ret

        kwargs['note'] = note
        kwargs['questions'] = quiz_from_keywords(note)
        kwargs['show_quiz'] = True

        return super(NoteQuizView, self).get_context_data(**kwargs)


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

    # If note thanks exceeds a threshold, create a Mechanical
    # Turk task to get some keywords for it
    if note.thanks == KEYWORD_MTURK_THRESHOLD:
        submit_extract_keywords_hit.delay(note)


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
    if request_user.is_authenticated() and note.user and note.user != request_user:
        NoteKarmaEvent.create_event(note.user, note, NoteKarmaEvent.HAD_NOTE_DOWNLOADED)


def downloaded_note(request, pk):
    """Record that somebody has flagged a note."""
    return ajax_pk_base(Note, request, pk, process_downloaded_note)


def edit_note_tags(request, pk):
    """
    Saves the posted string of tags
    """
    note = Note.objects.get(pk=pk)
    if request.method == "POST" and request.is_ajax() and note.allows_tags_by(request.user):
        note.tags.set(request.body)

        note_json = serializers.serialize('json', [note,])
        resp = json.loads(note_json)[0]
        resp['fields']['tags'] = list(note.tags.names())

        return HttpResponse(json.dumps(resp), mimetype="application/json")
    if request.method != "POST" or not request.is_ajax():
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'Invalid request'}),
                                      mimetype="application/json")
    else:
        return HttpResponseForbidden(json.dumps({'status': 'fail', 'message': 'Not permitted'}),
                                      mimetype="application/json")

