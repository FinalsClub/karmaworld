#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import random

from django.conf import settings
from django.forms import CharField
from django.forms import ValidationError

from ajax_select.fields import AutoCompleteField, AutoCompleteSelectWidget
from ajax_select.fields import AutoCompleteSelectField
from ajax_select_cascade.fields import AutoCompleteDependentSelectField

# generates DIV errors with appropriate classes
from django.utils.safestring import mark_safe
from karmaworld.utils.forms import NiceErrorModelForm
# supports handling autocomplete fields as a model object or a value
from karmaworld.utils.forms import ACFieldModelForm
# supports filling in Foreign Key fields with another ModelForm
from karmaworld.utils.forms import DependentModelForm

from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import Professor
from karmaworld.apps.courses.models import Department


class ProfessorForm(NiceErrorModelForm, ACFieldModelForm):
    """ Find or create a Professor. """
    # AutoCompleteField would make sense for these fields because it only
    # returns the value while AutoCompleteSelectField returns the object.
    # This way, Javascript on the front end can autofill the other field based
    # on the autocompletion of one field because the whole object is available.

    # first argument is ajax channel name, defined in models as LookupChannel.
    name = AutoCompleteSelectField('professor_object_by_name', help_text='',
        label=mark_safe('Professor\'s name <span class="required-field">(required)</span>'),
        # allows creating a new Professor on the fly
        required=False)
    email = AutoCompleteSelectField('professor_object_by_email', help_text='',
        label="Professor's email address",
        # allows creating a new Professor on the fly
        required=False)

    class Meta:
        model = Professor
        # order the fields
        fields = ('name', 'email')

    def _clean_distinct_field(self, field, value_required=False, *args, **kwargs):
        """
        Check to see if Professor model is found before grabbing the field.
        Ensure that if Professor was already found, the new field corresponds.

        In theory, Javascript could and should ensure this.
        In practice, better safe than incoherent.
        """
        oldprof = None
        if hasattr(self, 'instance') and self.instance and self.instance.pk:
            # Professor was already autocompleted. Save that object.
            oldprof = self.instance
        # Extract the field value, possibly replacing self.instance
        value = self._clean_field(field, *args, **kwargs)
        if value_required and not value:
            raise ValidationError('This field is required.')
        if oldprof and not value:
            # This field was not supplied, but another one determined the prof.
            # Grab field from prof model object.
            value = getattr(oldprof, field)
        if oldprof and self.instance != oldprof:
            # Two different Professor objects have been found across fields.
            raise ValidationError('It looks like two or more different Professors have been autocompleted.')

        return value

    def clean_name(self, *args, **kwargs):
        return self._clean_distinct_field('name', value_required=True, *args, **kwargs)

    def clean_email(self, *args, **kwargs):
        return self._clean_distinct_field('email', *args, **kwargs)


class DepartmentForm(NiceErrorModelForm, ACFieldModelForm):
    """ Find and create a Department given a School. """
    # first argument is ajax channel name, defined in models as LookupChannel.
    school = AutoCompleteSelectField('school_object_by_name',
                                     help_text='',
                                     plugin_options={'minLength': 3},
                                     label=mark_safe('School <span class="required-field">(required)</span>'))
    # first argument is ajax channel name, defined in models as LookupChannel.
    name = AutoCompleteDependentSelectField(
        'dept_object_by_name_given_school', help_text='',
        label=mark_safe('Department name <span class="required-field">(required)</span>'),
        # autocomplete department based on school
        dependsOn=school,
        # allows creating a new department on the fly
        required=False,
        widget_id='input_department_name'
    )

    class Meta:
        model = Department
        # order the fields
        fields = ('school', 'name')

    def clean_name(self, *args, **kwargs):
        """
        Extract the name from the Department object if it already exists.
        """
        name = self._clean_field('name', *args, **kwargs)
        # this might be unnecessary
        if not name:
            raise ValidationError('Cannot create a Department without a name.')
        return name


class CourseForm(NiceErrorModelForm, DependentModelForm):
    """ A course form which adds a honeypot and autocompletes some fields. """
    # first argument is ajax channel name, defined in models as LookupChannel.
    # note this AJAX field returns a field value, not a course object.
    name = AutoCompleteField('course_name_by_name', help_text='',
        label=mark_safe('Course name <span class="required-field">(required)</span>'))

    def __init__(self, *args, **kwargs):
        """ Add a dynamically named field. """
        super(CourseForm, self).__init__(*args, **kwargs)
        # insert honeypot into a random order on the form.
        idx = random.randint(0, len(self.fields))
        self.fields.insert(idx, settings.HONEYPOT_FIELD_NAME,
            CharField(required=False, label=mark_safe(settings.HONEYPOT_LABEL))
        )

    class Meta:
        model = Course
        # order the fields
        fields = ('name', 'url')
        model_fields = {
            # pass department data onto DepartmentForm
            'department': DepartmentForm,
            # pass professor data onto ProfessorForm
            'professor': ProfessorForm,
        }

    def clean(self, *args, **kwargs):
        """ Honeypot validation. """

        # Call ModelFormMixin or whoever normally cleans house.
        cleaned_data = super(CourseForm, self).clean(*args, **kwargs)

        # Check the honeypot
        # parts of this code borrow from
        # https://github.com/sunlightlabs/django-honeypot
        hfn = settings.HONEYPOT_FIELD_NAME
        formhoneypot = cleaned_data.get(hfn, None)
        if formhoneypot and (formhoneypot != settings.HONEYPOT_VALUE):
            # Highlight the failure to follow instructions.
            self._errors[hfn] = [settings.HONEYPOT_ERROR]
            del cleaned_data[hfn]
        return cleaned_data
