#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Views for the KarmaNotes Courses app """

import json
from django.conf import settings
from django.core import serializers
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from django.views.generic import View
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView

from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School
from karmaworld.apps.courses.forms import CourseForm
from karmaworld.apps.notes.models import Note
from karmaworld.apps.users.models import CourseKarmaEvent
from karmaworld.apps.notes.forms import FileUploadForm
from karmaworld.utils import ajax_increment, format_session_increment_field
from django.contrib import messages

FLAG_FIELD = 'flags'
USER_PROFILE_FLAGS_FIELD = 'flagged_courses'


# https://docs.djangoproject.com/en/1.5/topics/class-based-views/mixins/#an-alternative-better-solution
class CourseListView(View):
    """
    Composite view to list all courses and processes new course additions.
    """

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return CourseListSubView.as_view()(request, *args, **kwargs)
        # Cache the homepage for non-authenicated users
        else:
            return cache_page(CourseListSubView.as_view(), 60 * 60)(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ret = CourseAddFormView.as_view()(request, *args, **kwargs)
        # Check to see if the form came back with errors.
        if hasattr(ret, 'context_data') and \
           ret.context_data.has_key('form') and \
           not ret.context_data['form'].is_valid():
            # Invalid form. Render as if by get(), but replace the form.
            badform = ret.context_data['form']
            request.method = 'GET' # trick get() into returning something
            ret = self.get(request, *args, **kwargs)
            # Replace blank form with invalid form.
            ret.context_data['course_form'] = badform
            ret.context_data['jump_to_form'] = True
        else:
            messages.add_message(request, messages.SUCCESS, 'You\'ve just created this course. Nice!')
        return ret


class CourseListSubView(ListView):
    """ Lists all courses. Called by CourseListView. """
    model = Course

    def get_queryset(self):
        return Course.objects.all().select_related('note_set', 'school', 'department', 'department__school')

    def get_context_data(self, **kwargs):
        """ Add the CourseForm to ListView context """
        # get the original context
        context = super(CourseListSubView, self).get_context_data(**kwargs)
        # get the total number of notes
        context['note_count'] = Note.objects.count()
        # get the course form for the form at the bottom of the homepage
        context['course_form'] = CourseForm()

        # Include settings constants for honeypot
        for key in ('HONEYPOT_FIELD_NAME', 'HONEYPOT_VALUE'):
            context[key] = getattr(settings, key)

        return context


class CourseAddFormView(CreateView):
    """ Processes new course additions. Called by CourseListView. """
    model = Course
    form_class = CourseForm

    def get_template_names(self):
        """ template_name must point back to CourseListView url """
        # TODO clean this up. "_list" template might come from ListView above.
        return ['courses/course_list.html',]


class CourseDetailView(DetailView):
    """ Class-based view for the course html page """
    model = Course
    context_object_name = u"course" # name passed to template

    def get_context_data(self, **kwargs):
        """ filter the Course.note_set to return no Drafts """
        kwargs = super(CourseDetailView, self).get_context_data()
        kwargs['note_set'] = self.object.note_set.filter(is_hidden=False)

        # For the Filepicker Partial template
        kwargs['file_upload_form'] = FileUploadForm()

        if self.request.user.is_authenticated():
            try:
                self.request.user.get_profile().flagged_courses.get(pk=self.object.pk)
                kwargs['already_flagged'] = True
            except ObjectDoesNotExist:
                pass

        return kwargs


class AboutView(TemplateView):
    """ Display the About page with the Schools leaderboard """
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        """ get the list of schools with the most files for leaderboard """
        if 'schools' not in kwargs:
            kwargs['schools'] = School.objects.filter(file_count__gt=0).order_by('-file_count')[:20]
        return kwargs


def school_list(request):
    """ Return JSON describing Schools that match q query on name """
    if not (request.method == 'POST' and request.is_ajax()
                        and request.POST.has_key('q')):
        #return that the api call failed
        return HttpResponseBadRequest(json.dumps({'status':'fail'}), mimetype="application/json")

    # if an ajax get request with a 'q' name query
    # get the schools as a id name dict,
    _query = request.POST['q']
    matching_school_aliases = list(School.objects.filter(alias__icontains=_query))
    matching_school_names = sorted(list(School.objects.filter(name__icontains=_query)[:20]),key=lambda o:len(o.name))
    _schools = matching_school_aliases[:2] + matching_school_names
    schools = [{'id': s.id, 'name': s.name} for s in _schools]

    # return as json
    return HttpResponse(json.dumps({'status':'success', 'schools': schools}), mimetype="application/json")


def school_course_list(request):
    """Return JSON describing courses we know of at the given school
     that match the query """
    if not (request.method == 'POST' and request.is_ajax()
                        and request.POST.has_key('q')
                        and request.POST.has_key('school_id')):
        # return that the api call failed
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'query parameters missing'}),
                                    mimetype="application/json")

    _query = request.POST['q']
    try:
      _school_id = int(request.POST['school_id'])
    except:
      return HttpResponseBadRequest(json.dumps({'status': 'fail',
                                              'message': 'could not convert school id to integer'}),
                                  mimetype="application/json")

    # Look up the school
    try:
        school = School.objects.get(id__exact=_school_id)
    except (MultipleObjectsReturned, ObjectDoesNotExist):
        return HttpResponseBadRequest(json.dumps({'status': 'fail',
                                                'message': 'school id did not match exactly one school'}),
                                    mimetype="application/json")

    # Look up matching courses
    _courses = Course.objects.filter(school__exact=school.id, name__icontains=_query)
    courses = [{'name': c.name} for c in _courses]

    # return as json
    return HttpResponse(json.dumps({'status':'success', 'courses': courses}),
                        mimetype="application/json")


def school_course_instructor_list(request):
    """Return JSON describing instructors we know of at the given school
       teaching the given course
       that match the query """
    if not(request.method == 'POST' and request.is_ajax()
                        and request.POST.has_key('q')
                        and request.POST.has_key('course_name')
                        and request.POST.has_key('school_id')):
        # return that the api call failed
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'query parameters missing'}),
                                    mimetype="application/json")

    _query = request.POST['q']
    _course_name = request.POST['course_name']
    try:
      _school_id = int(request.POST['school_id'])
    except:
      return HttpResponseBadRequest(json.dumps({'status': 'fail',
                                              'message':'could not convert school id to integer'}),
                                  mimetype="application/json")

    # Look up the school
    try:
        school = School.objects.get(id__exact=_school_id)
    except (MultipleObjectsReturned, ObjectDoesNotExist):
        return HttpResponseBadRequest(json.dumps({'status': 'fail',
                                                  'message': 'school id did not match exactly one school'}),
                                    mimetype="application/json")

    # Look up matching courses
    _courses = Course.objects.filter(school__exact=school.id,
                                     name__exact=_course_name,
                                     instructor_name__icontains=_query)
    instructors = [{'name': c.instructor_name, 'url': c.get_absolute_url()} for c in _courses]

    # return as json
    return HttpResponse(json.dumps({'status':'success', 'instructors': instructors}),
                        mimetype="application/json")


def process_course_flag_events(request_user, course):
    # Take a point away from person flagging this course
    if request_user.is_authenticated():
        CourseKarmaEvent.create_event(request_user, course, CourseKarmaEvent.GIVE_FLAG)


def flag_course(request, pk):
    """Record that somebody has flagged a note."""
    return ajax_increment(Course, request, pk, FLAG_FIELD, USER_PROFILE_FLAGS_FIELD, process_course_flag_events)


def edit_course(request, pk):
    """
    Saves the edited course content
    """
    if request.method == "POST" and request.is_ajax():
        course = Course.objects.get(pk=pk)
        original_name = course.name
        course_form = CourseForm(request.POST or None, instance=course)

        if course_form.is_valid():
            course_form.save()

            course_json = serializers.serialize('json', [course,])
            resp = json.loads(course_json)[0]

            if (course.name != original_name):
                course.set_slug()
                resp['fields']['new_url'] = course.get_absolute_url()

            return HttpResponse(json.dumps(resp), mimetype="application/json")
        else:
            return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'Validation error',
                                          'errors': course_form.errors}),
                                          mimetype="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'Invalid request'}),
                                      mimetype="application/json")
