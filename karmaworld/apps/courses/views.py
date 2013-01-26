#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import json

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


def school_list(request):
    """ Return JSON describing Schools that match q query on name """
    if request.method == 'GET' and request.is_ajax() \
                        and request.GET.has_key('q'):
        # if an ajax get request with a 'q' name query
        # get the list of schools that match and return
        schools = School.objects.filter(name__icontains=request.GET['q'])[:4]
        return json.dump({'status':'success', 'schools': schools})
    else:
        # else return that the api call failed
        return json.dump({'status':'fail'})
