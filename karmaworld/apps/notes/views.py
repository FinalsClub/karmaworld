#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import View
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404

from karmaworld.apps.notes.models import Note
from karmaworld.apps.notes.forms import NoteForm


class NoteDetailView(DetailView):
    """ Class-based view for the note html page """
    model = Note
    context_object_name = u"note" # name passed to template

    def get_context_data(self, **kwargs):
        """ Generate custom context for the page rendering a Note
            + if pdf, set the `pdf` flag
        """
        #kwargs['file_url'] = os.path.basename(_path)
        #kwargs['hostname'] = Site.objects.get_current()

        def is_pdf(self):
            _path = self.object.note_file.name
            _, _extension = os.path.splitext(_path)
            if _extension.lower() == '.pdf':
                return True
            return False

        kwargs['pdf'] = is_pdf(self)

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
        # FIXME: There may be an undocumented,
        #   but better way of handling media files in django

        kwargs['pdf_path'] = "{0}{1}".format(settings.MEDIA_URL,
            os.path.basename(self.object.note_file.name))

        return super(PDFView, self).get_context_data(**kwargs)
