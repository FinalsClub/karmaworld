#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

import datetime

from django.http import HttpResponse
from django.views.generic import CreateView
from django.views.generic.edit import ProcessFormView
from django.views.generic.edit import ModelFormMixin

from karmaworld.apps.document_upload.models import RawDocument
from karmaworld.apps.document_upload.forms import RawDocumentForm

def save_fp_upload(request):
    r_d_f = RawDocumentForm(request.POST)
    if r_d_f.is_valid():
        model_instance = r_d_f.save(commit=False)
        model_instance.uploaded_at = datetime.datetime.utcnow()
        model_instance.save()
        return HttpResponse({'success'})
    else:
        return HttpResponse(r_d_f.errors, status=400)



class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return self.render_to_json_response(data)
        else:
            return response

class RawDocumentCreate(AjaxableResponseMixin, CreateView):
    model = RawDocument
