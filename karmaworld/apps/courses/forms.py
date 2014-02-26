#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import random

from django.conf import settings
from django.forms import ModelForm
from django.forms import CharField
from django.forms.util import ErrorList

from ajax_select.fields import AutoCompleteSelectField
from ajax_select.fields import AutoCompleteSelectWidget
from ajax_select_cascade.fields import AutoCompleteDependentSelectField
from ajax_select_cascade.fields import AutoCompleteDependentSelectWidget

from karmaworld.apps.courses.models import Course


# Django hard codes CSS attributes into ModelForm returned ErrorList
# https://github.com/django/django/blob/1.5.5/django/forms/util.py#L54-L60
# https://docs.djangoproject.com/en/1.5/ref/forms/api/#customizing-the-error-list-format
# so this unfortunately doesn't do anything with ModelForms:
# https://docs.djangoproject.com/en/1.5/ref/forms/api/#django.forms.Form.error_css_class
class CSSErrorList(ErrorList):
    """ Override ErrorList classes. """
    def as_ul(self, *args, **kwargs):
        errorhtml = super(CSSErrorList, self).as_ul(*args, **kwargs)
        # insert <label> around the error
        errorhtml = errorhtml.replace('<li>', "<li><label class='validation_error'>")
        errorhtml = errorhtml.replace('</li>', '</label></li>')
        # replace hard coded "errorlist" with something in our CSS:
        errorhtml = errorhtml.replace('errorlist', 'validation_error')
        return errorhtml


class NiceErrorModelForm(ModelForm):
    """ By default use CSSErrorList for displaying errors. """
    def __init__(self, *args, **kwargs):
        if 'error_class' not in kwargs:
            kwargs['error_class'] = CSSErrorList
        super(NiceErrorModelForm, self).__init__(*args, **kwargs)


class CourseForm(NiceErrorModelForm):
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

    def __init__(self, *args, **kwargs):
        """ Add a dynamically named field. """
        super(CourseForm, self).__init__(*args, **kwargs)
        # insert honeypot into a random order on the form.
        idx = random.randint(0, len(self.fields))
        self.fields.insert(idx, settings.HONEYPOT_FIELD_NAME,
            CharField(required=False, label=settings.HONEYPOT_LABEL)
        )

    class Meta:
        model = Course
        # order the fields
        fields = ('school', 'department', 'name', 'instructor_name',
                  'instructor_email', 'url')

    def clean(self, *args, **kwargs):
        """ Additional form validation. """

        # Call ModelFormMixin or whoever normally cleans house.
        cleaned_data = super(CourseForm, self).clean(*args, **kwargs)

        # parts of this code borrow from
        # https://github.com/sunlightlabs/django-honeypot
        hfn = settings.HONEYPOT_FIELD_NAME
        formhoneypot = cleaned_data.get(hfn, None)
        if formhoneypot and (formhoneypot != settings.HONEYPOT_VALUE):
            # Highlight the failure to follow instructions.
            self._errors[hfn] = [settings.HONEYPOT_ERROR]
            del cleaned_data[hfn]
        return cleaned_data
