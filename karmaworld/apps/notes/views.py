#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404

from karmaworld.apps.notes.models import Note
from karmaworld.apps.notes.forms import NoteForm


class NoteDetailView(DetailView):
    """ Class-based view for the note html page """
    model = Note
    context_object_name = u"note" # name passed to template


class NoteSaveView(FormView, SingleObjectMixin):
    """ Save a Note and then view the page, 
        behaves the same as NoteDetailView, except for saving the
        NoteForm ModelForm
    """
    # TODO: implement def form_invalid for returning a form with input and error
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
        self.object.name = form.cleaned_data['name']
        self.object.year = form.cleaned_data['year']
        # use *arg expansion to pass tags a list of tags
        self.object.tags.add(*form.cleaned_data['tags'])
        self.object.save()
        return super(NoteSaveView, self).form_valid(form)

    def form_invalid(self, form):
        """ Do stuff when the form is invalid !!! TODO """
        print "running form_invalid"
        print self.form
        print self.form.errors


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


def raw_file(request, pk):
    """ Display the raw html from a Note object for embedding in an iframe """
    note = get_object_or_404(Note, pk=pk)
    return HttpResponse(note.html)
