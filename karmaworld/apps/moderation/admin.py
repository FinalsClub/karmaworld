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

# Structure views of Course objects
class CourseModerator(CourseAdmin):
    date_heirarchy = 'updated_at'
    # Identify fields to display on the Change page
    list_display = ('name', 'flags', 'school', 'academic_year', 'created_at', 'updated_at', 'instructor_name')
    # Sort by highest number of flags first, and then by date for ties.
    ordering = ('-flags', '-updated_at')
    # Enable resetting flags
    actions = (reset_flags,)

# Structure views of Note objects
class NoteModerator(NoteAdmin):
    date_heirarchy = 'uploaded_at'
    # Identify fields to display on the Change page
    list_display = ('name', 'flags', 'course', 'uploaded_at', 'ip')
    # Sort by highest number of flags first, and then by date for ties
    ordering = ('-flags', '-uploaded_at')
    # Enable resetting flags
    actions = (reset_flags,)

moderator.site.register(Course, CourseModerator)
moderator.site.register(Note, NoteModerator)
