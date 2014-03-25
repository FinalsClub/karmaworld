#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration page for moderators """

from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.admin import CourseAdmin
from karmaworld.apps.notes.models import Note
from karmaworld.apps.notes.admin import NoteAdmin
from karmaworld.apps.moderation import moderator


# Create a simple action to reset flags to zero.
# https://docs.djangoproject.com/en/1.4/ref/contrib/admin/actions/
def reset_flags(modeladmin, request, queryset):
    queryset.update(flags=0)
reset_flags.short_description = "Reset flags to 0"


# Create a simple action to set is_hidden
def hide_notes(modeladmin, request, queryset):
    queryset.update(is_hidden=True)
hide_notes.short_description = "Hide selected notes"


# Create a simple action to unset is_hidden
def show_notes(modeladmin, request, queryset):
    queryset.update(is_hidden=False)
show_notes.short_description = "Show selected notes"


# Structure views of Course objects
class CourseModerator(CourseAdmin):
    date_heirarchy = 'updated_at'
    # Identify fields to display on the Change page
    list_display = ('name', 'flags', 'url', 'updated_at', 'department','professor')
    # Sort by highest number of flags first, and then by date for ties.
    ordering = ('-flags', '-updated_at')
    # Enable resetting flags
    actions = (reset_flags,)


# Structure views of Note objects
class NoteModerator(NoteAdmin):
    date_heirarchy = 'uploaded_at'
    # Identify fields to display on the Change page
    list_display = ('name', 'flags', 'course', 'is_hidden', 'uploaded_at', 'ip')
    # Sort by highest number of flags first, and then by date for ties
    ordering = ('-flags', '-uploaded_at')
    # Enable resetting flags
    actions = (reset_flags, hide_notes, show_notes)

# Structure views of Department objects
class DepartmentModerator(NoteAdmin):
    date_heirarchy = 'uploaded_at'
    # Identify fields to display on the Change page
    list_display = ('name', 'school', 'url')
    # Sort by highest number of flags first, and then by date for ties
    ordering = ('-flags', '-uploaded_at')
    # Enable resetting flags
    actions = (reset_flags,)

# Structure views of Professor objects
class ProfessorModerator(NoteAdmin):
    date_heirarchy = 'uploaded_at'
    # Identify fields to display on the Change page
    list_display = ('name', 'email')
    # Sort by highest number of flags first, and then by date for ties
    ordering = ('-flags', '-uploaded_at')
    # Enable resetting flags
    actions = (reset_flags,)

moderator.site.register(Course, CourseModerator)
moderator.site.register(Note, NoteModerator)
moderator.site.register(Department, DepartmentModerator)
moderator.site.register(Professor, ProfessorModerator)
