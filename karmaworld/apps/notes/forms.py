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

    def save(self, *args, **kwargs):
        # TODO: use transaction.atomic for this when we switch to Django 1.6+
        print self.cleaned_data
        instance = super(NoteForm, self).save(*args, **kwargs)
        instance.tags.set(*self.cleaned_data['tags'])
        if instance.is_hidden:
            instance.is_hidden = False
            instance.save()
        if self.cleaned_data.get('html'):
            try:
                note_markdown = instance.notemarkdown
            except NoteMarkdown.DoesNotExist:
                note_markdown = NoteMarkdown(note=instance)
            note_markdown.html = self.cleaned_data['html']
            note_markdown.full_clean()
            note_markdown.save()
        return instance

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
