#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Views for the KarmaNotes Courses app """

import json

from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView
from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import ListView

from karmaworld.apps.courses.forms import CourseForm
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School
from karmaworld.apps.notes.models import Note


class CourseListView(ListView, ModelFormMixin, ProcessFormView):
    """ Simple ListView for the front page that includes the CourseForm """
    model = Course
    form_class = CourseForm
    object = Course()

    def get_context_data(self, **kwargs):
        """ Add the CourseForm to ListView context """
        # get the original context
        context = super(CourseListView, self).get_context_data(**kwargs)
        # get the total number of notes
        context['note_count'] = Note.objects.count()
        # get the course form for the form at the bottom of the homepage
        context['course_form'] = kwargs.get('course_form', CourseForm())
        if context['course_form'].errors:
            # if there was an error in the form
            context['jump_to_form'] = True

        return context

    def get_success_url(self):
        """ On form submission success, redirect to what url """
        return u'/{school_slug}/{course_slug}'.format(
                school_slug=self.object.school.slug,
                course_slug=self.object.slug
            )

    def form_invalid(self, form, **kwargs):
        """ override form_invalid to populate object_list on redirect """
        kwargs['is_error'] = True
        kwargs['course_form'] = form
        self.object_list = self.get_queryset()
        kwargs['object_list'] = self.object_list
        return self.render_to_response(self.get_context_data(**kwargs))



class CourseDetailView(DetailView):
    """ Class-based view for the course html page """
    model = Course
    context_object_name = u"course" # name passed to template


class AboutView(TemplateView):
    """ Display the About page with the Schools leaderboard """
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        """ get the list of schools with the most files for leaderboard """
        context = { 'params': kwargs, \
                    'schools': School.objects.all()[:3] }
        return context


def school_list(request):
    """ Return JSON describing Schools that match q query on name """
    if request.method == 'POST' and request.is_ajax() \
                        and request.POST.has_key('q'):
        # if an ajax get request with a 'q' name query
        # get the schools as a id name dict,
        _query = request.POST['q']
        matching_school_aliases = list(School.objects.filter(alias__icontains=_query))
        matching_school_names = list(School.objects.filter(name__icontains=_query)[:20])
        _schools = matching_school_aliases[:2] + matching_school_names
        schools = [{'id': s.id, 'name': s.name} for s in _schools]

        # return as json
        return HttpResponse(json.dumps({'status':'success', 'schools': schools}), mimetype="application/json")
    else:
        # else return that the api call failed
        return HttpResponse(json.dumps({'status':'fail'}), mimetype="application/json")
