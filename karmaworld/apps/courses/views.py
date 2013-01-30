#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import json

from django.http import HttpResponse
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
