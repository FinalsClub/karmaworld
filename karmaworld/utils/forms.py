#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation


import inspect

from django.forms import ModelForm
from django.forms.util import ErrorList
from django.utils.safestring import mark_safe


# helper function to determine if field of form is ManyToMany.
def is_m2m(form, field):
    modelfield = getattr(form.Meta.model, field)
    # check by contract (quacks like a duck) rather than instance checking
    return hasattr(modelfield, 'through') and hasattr(modelfield, 'field')


# Django hard codes CSS attributes into ModelForm returned ErrorList
# https://github.com/django/django/blob/1.5.5/django/forms/util.py#L54-L60
# https://docs.djangoproject.com/en/1.5/ref/forms/api/#customizing-the-error-list-format
# so this unfortunately doesn't do anything with ModelForms:
# https://docs.djangoproject.com/en/1.5/ref/forms/api/#django.forms.Form.error_css_class
class CSSErrorList(ErrorList):
    """ Override ErrorList classes. """
    def as_ul(self, *args, **kwargs):
        # It might be more efficient to rewrite this properly rather than string
        # hack it. For now, this is more flexible to changes in Django.
        errorhtml = super(CSSErrorList, self).as_ul(*args, **kwargs)
        # insert <label> around the error
        errorhtml = errorhtml.replace('<li>', "<li><label class='validation_error'>")
        errorhtml = errorhtml.replace('</li>', '</label></li>')
        # replace hard coded "errorlist" with something in our CSS:
        errorhtml = errorhtml.replace('errorlist', 'validation_error')
        return errorhtml


class NiceErrorModelForm(ModelForm):
    """ By default use CSSErrorList for displaying errors and prefix fields. """
    def __init__(self, *args, **kwargs):
        if 'prefix' not in kwargs:
            # extract class name. this is ugly because Django magic classes.
            # use class name as prefix.
            kwargs['prefix'] = str(type(self)).split('.')[-1].split("'")[0]
        if 'error_class' not in kwargs:
            kwargs['error_class'] = CSSErrorList
        super(NiceErrorModelForm, self).__init__(*args, **kwargs)


class ACFieldModelForm(ModelForm):
    """
    Treats an AutoCompleteSelectField as either a field or a model instance.

    Such a field will either find a result or create a new instance to hold the
    result, so the concept of a required Field is a bit different. Ensure that
    required=False on any AutoComplete*Fields used in this way.

    This should be used in the correct clean function in the subclass like so:
    def clean_fieldname(self, *args, **kwargs):
        return self._clean_field('fieldname', *args, **kwargs)
    """
    def _clean_field(self, field, *args, **kwargs):
        """
        Given a form field name, decide if the form field contains a model.
        """
        # If the object already exists, its cleaned field will contain an object
        modelobject = self.cleaned_data.get(field, None)
        if modelobject:
            # tell this Form the object already exists in the database
            self.instance = modelobject
            # return the appropriate value for this field.
            return getattr(modelobject, field)
        # Otherwise we need to extract the field's value from the form by hand.
        return self.data.get(self.add_prefix(field + '_text'), None)


class DependentModelForm(ModelForm):
    """
    Support sending POST data to other ModelForms and returning their objects.

    Include a model_fields dictionary in Meta, which maps ForeignKey attributes
    to a corresponding ModelForm. Assuming a Car model has fields color, year,
    engine, and make, with the latter two being FKs that have corresponding
    ModelForms, it's Meta class might look like this:
    class Meta:
        model = Car
        fields = ('color', 'year')
        model_fields = { 'engine': EngineModelForm, 'make': MakeModelForm }
    """
    def __init__(self, *args, **kwargs):
        """ Clears cached modelforms. """
        # Prefix is practically required when using multiple forms against the
        # same POST data.
        if 'prefix' not in kwargs:
            # extract class name. this is ugly because Django magic classes.
            # use class name as prefix.
            kwargs['prefix'] = str(type(self)).split('.')[-1].split("'")[0]
        # indicate no dependent form objects have been made
        self.dependent_modelforms = {}
        self.dependent_modelforms_data = {}
        super(DependentModelForm, self).__init__(*args, **kwargs)

    def _get_forms(self):
        """ Memoize dependent form objects. """
        # Determine if there is data.
        with_data = True if self.data else False
        # Memoize data separately if there is or is not data.
        data = (self.data,) if with_data else tuple()
        memo = self.dependent_modelforms_data if with_data else \
               self.dependent_modelforms
        if not memo:
            # Any attributes which need a model object (defined in
            # Meta.model_fields) will have ModelForms created at this time.
            for attribute, modelform in self.Meta.model_fields.iteritems():
                # Mebbe pass POST data into the foreign model form.
                memo[attribute] = modelform(*data)
        return memo

    def _media(self):
        """ Render all dependent form media as well as this form's. """
        # too bad Django doesn't have a nice way to process this?
        # prepare base Media object.
        superself = super(DependentModelForm, self)
        if inspect.ismethod(superself.media):
            selfmedia = superself.media()
        else:
            selfmedia = superself.media

        # search through each dependent form for media
        for modelform in self._get_forms().itervalues():
            if inspect.ismethod(modelform.media):
                media = modelform.media()
            else:
                media = modelform.media
            # update CSS dict
            selfmedia.add_css(media._css)
            # uniquely concatenate JS sources
            selfmedia.add_js(media._js)

        # send back the results
        return selfmedia

    # https://docs.djangoproject.com/en/1.5/topics/forms/media/#media-as-a-dynamic-property
    media = property(_media)

    def is_valid(self, *args, **kwargs):
        """ Check all subforms for validity and then this form. """
        all_valid = True
        # Perform validation and error checking for each ModelForm.
        for attribute, modelform in self._get_forms().iteritems():
            if not modelform.is_valid():
                all_valid = False

        # Process this form's validity to generate errors.
        # This form is invalid if it is invalid or its subforms are invalid.
        return super(DependentModelForm, self).is_valid(*args, **kwargs) and all_valid

    def _post_clean(self, *args, **kwargs):
        """ Inject objects created from required ModelForms. """
        super(DependentModelForm, self)._post_clean(*args, **kwargs)

        # If self.instance has not been created by _post_clean, create it now.
        # This happens when only model_fields are present and no fields.
        try:
            str(self.instance)
        except:
            self.instance = self.Meta.model()

        # Don't create objects if this form is not valid.
        if not self.is_valid():
            return

        # create foreign model object and associate it internally here
        for attribute, modelform in self._get_forms().iteritems():
            # handle ManyToMany versus ForeignKey
            if not is_m2m(self, attribute):
                # Handle Foreign Key, assign object directly to attribute
                setattr(self.instance, attribute, modelform.save())

    def save(self, *args, **kwargs):
        """ Handle ManyToMany objects. """
        instance = super(DependentModelForm, self).save(*args, **kwargs)

        # Check for and update any M2M model_fields
        if hasattr(self.instance, 'pk') and self.instance.pk:
            # objects were created during commit. associate M2M now.
            for attribute, modelform in self._get_forms().iteritems():
                # handle ManyToMany versus ForeignKey
                if is_m2m(self, attribute):
                    # use add() to create association between models.
                    getattr(instance, attribute).add(modelform.save())
        else:
            # objects not yet in database. save for later.
            # reference to save_m2m deferred function from BaseModelForm.save()
            old_save_m2m = self.save_m2m

            # write a new save_m2m with Python closure power!
            def save_m2m():
                # call "super"
                old_save_m2m()
                # associate M2M objects with self instance
                for attribute, modelform in self._get_forms().iteritems():
                    # ManyToMany contract test.
                    # use add() to create association between models.
                    objattr = getattr(instance, attribute, None)
                    if objattr and hasattr(objattr, 'add'):
                        objattr.add(modelform.save())

            # save function for later just as BaseModelForm.save() does
            self.save_m2m = save_m2m

        # passthrough instance
        return instance

    def _render_dependencies_first(self, method, *args, **kwargs):
        """ Render dependent forms prior to rendering this form. """
        html = ''
        # render each form
        for modelform in self._get_forms().itervalues():
            html += getattr(modelform, method)(*args, **kwargs)
        # render this form
        supermethod = getattr(super(DependentModelForm, self), method)
        html += supermethod(*args, **kwargs)
        return mark_safe(html)

    def as_p(self, *args, **kwargs):
        return self._render_dependencies_first('as_p', *args, **kwargs)
    def as_ul(self, *args, **kwargs):
        return self._render_dependencies_first('as_ul', *args, **kwargs)
    def as_table(self, *args, **kwargs):
        return self._render_dependencies_first('as_table', *args, **kwargs)
