#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.conf import settings
from django.forms import ModelForm
from django.forms import CharField

from karmaworld.apps.courses.models import Course

class CourseForm(ModelForm):

    def __init__(self, *args, **kwargs):
        """ Add a dynamically named field. """
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields[settings.HONEYPOT_FIELD_NAME] = CharField(required=False)

    class Meta:
        model = Course
        fields = ('name', 'school', 'url', 'instructor_name', \
                  'instructor_email')

    def clean(self, *args, **kwargs):
        """ Additional form validation. """

        # Call ModelFormMixin or whoever normally cleans house.
        cleaned_data = super(CourseForm, self).clean(*args, **kwargs)

        # parts of this code borrow from
        # https://github.com/sunlightlabs/django-honeypot
        hfn = settings.HONEYPOT_FIELD_NAME
        formhoneypot = cleaned_data.get(hfn, None)
        if formhoneypot and (formhoneypot != settings.HONEYPOT_VALUE):
            # Highlight a failure to follow instructions.
            # When the template dynamically generates the form, replace
            # 'honeypot' with hfn
            self._errors['honeypot'] = [u'You did not follow directions.']
            del cleaned_data[hfn]
        return cleaned_data
