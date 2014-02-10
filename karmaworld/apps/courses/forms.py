#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.forms import ModelForm

from ajax_select.fields import AutoCompleteSelectField
from ajax_select.fields import AutoCompleteSelectWidget
from ajax_select_cascade.fields import AutoCompleteDependentSelectField
from ajax_select_cascade.fields import AutoCompleteDependentSelectWidget

from karmaworld.apps.courses.models import Course

class CourseForm(ModelForm):
    school = AutoCompleteSelectField(
        'school',
        widget=AutoCompleteSelectWidget(
            'school',
            attrs={'id': 'dom_autocomplete_school'}
        )
    )
    department = AutoCompleteDependentSelectField(
        'dept_given_school',
        widget=AutoCompleteDependentSelectWidget(
            'dept_given_school',
             attrs={'data-upstream-id': 'dom_autocomplete_school'},
        )
    )
    class Meta:
        model = Course
        # order the fields
        fields = ('school', 'department', 'name', 'instructor_name',
                  'instructor_email', 'url')
