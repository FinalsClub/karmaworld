#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
from django.forms import ModelForm, IntegerField, HiddenInput, Form, CharField, Textarea
from django.forms import TextInput
from django_filepicker.widgets import FPFileWidget
from django.template.loader import render_to_string
from wysihtml5.widgets import RichTextEditor

from karmaworld.apps.notes.models import Note, NoteMarkdown


class NoteForm(ModelForm):
    html = CharField(widget=RichTextEditor)

    class Meta:
        model = Note
        fields = ('name', 'tags', 'html')
        widgets = {
          'name': TextInput()
        }

class NoteDeleteForm(Form):
    note = IntegerField(widget=HiddenInput())

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
