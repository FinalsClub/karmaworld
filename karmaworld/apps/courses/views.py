#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import json

from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import CreateView
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import ProcessFormView
from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import BaseListView

from karmaworld.apps.courses.forms import CourseForm
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School


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


class CourseSaveView(ModelFormMixin, ProcessFormView):
    """ Save a course form and then view that course page """
    # TODO: make this not use a genericview
    form_class = CourseForm
    model = Course
    template_name = 'course/course_detail.html'
    object = Course()

    def get_success_url(self):
        """ On form submission success, redirect to what url """
        return u'/{school_slug}/{course_slug}'.format(
                school_slug=self.object.school.slug,
                course_slug=self.object.slug
            )

    def form_invalid(self, form):
        # TODO: create stand-alone version of form with errors
        print "form invalid"
        print dir(form)
        print form.errors
        print "\n\n"


def school_list(request):
    """ Return JSON describing Schools that match q query on name """
    if request.method == 'POST' and request.is_ajax() \
                        and request.POST.has_key('q'):
        # if an ajax get request with a 'q' name query
        # get the schools as a id name dict,
        schools = [{'id': s.id, 'name': s.name} for s in \
              School.objects.filter(name__icontains=request.POST['q'])[:4]]
        # return as json
        return HttpResponse(json.dumps({'status':'success', 'schools': schools}), mimetype="application/json")
    else:
        # else return that the api call failed
        return HttpResponse(json.dump({'status':'fail'}), mimetype="application/json")
