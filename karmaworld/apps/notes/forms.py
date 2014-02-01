#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.forms import ModelForm
from django.forms import TextInput

from django_filepicker.forms import FPFileField
from django_filepicker.widgets import FPFileWidget

from karmaworld.apps.notes.models import Note

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ('name', 'tags', 'year',)
        widgets = {
          'name': TextInput()
        }

class FileUploadForm(ModelForm):
    auto_id = False
    class Meta:
        model = Note
        fields = ('fp_file',)
        widgets = {
          'fp_file': FPFileWidget(attrs={
                       'id': 'filepicker-file-upload',
                     }),
        }
