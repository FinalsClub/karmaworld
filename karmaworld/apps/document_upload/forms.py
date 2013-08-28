#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

from django.forms import ModelForm

from karmaworld.apps.document_upload.models import RawDocument

class RawDocumentForm(ModelForm):
    class Meta:
        model = RawDocument
        fields = ('name', 'tags', 'course', 'fp_file')
