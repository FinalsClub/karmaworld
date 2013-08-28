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
