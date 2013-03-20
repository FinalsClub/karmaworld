#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.forms import ModelForm
from django.forms import TextInput

from karmaworld.apps.notes.models import Note

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ('name', 'tags', 'year',)
        widgets = {
          'name': TextInput()
        }
