#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.forms import ModelForm

from karmaworld.apps.notes.models import Note

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ('name', 'tags', 'desc',)
