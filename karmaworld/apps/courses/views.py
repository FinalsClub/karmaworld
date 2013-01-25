#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.views.generic import DetailView
from django.views.generic import TemplateView

from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School

class CourseDetailView(DetailView):
    """ Class-based view for the course html page """

    model = Course
    # name passed to template
    context_object_name = u"course"


class AboutView(TemplateView):
    """ Display the About page with the Schools leaderboard """
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        """ get the list of schools with the most files for leaderboard """
        context = { 'params': kwargs, \
                    'schools': School.objects.all()[:3] }
        return context
