#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.forms import ModelForm

from karmaworld.apps.courses.models import Course

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'school', 'desc', 'url', 'instructor_name', \
                'instructor_email')

