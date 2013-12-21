#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration configuration for notes """

from django.contrib import admin

from karmaworld.apps.notes.models import Note

class NoteAdmin(admin.ModelAdmin):
    """ an Admin handler for the Note model that handles autocomplete to Course 
    """
    raw_id_fields = ('course',)
    autocomplete_lookup_fields = {
        'fk': ['course']
    }

admin.site.register(Note, NoteAdmin)
