#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration configuration for courses """

from django.contrib import admin

from karmaworld.apps.courses.models import Course

class CourseAdmin(admin.ModelAdmin):
    """ an Admin handler for the Course model that handles fk search """
    raw_id_fields = ('school',)
    autocomplete_lookup_fields = {
        'fk': ['school']
    }

admin.site.register(Course, CourseAdmin)
