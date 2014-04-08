#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration configuration for courses """

import reversion

from django.contrib import admin

from karmaworld.apps.courses.models import School
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import Professor
from karmaworld.apps.courses.models import ProfessorAffiliation

class CourseAdmin(reversion.VersionAdmin, admin.ModelAdmin):
    """ an Admin handler for the Course model that handles fk search """
    raw_id_fields = ('school',)
    autocomplete_lookup_fields = {
        'fk': ['school']
    }
class DepartmentAdmin(reversion.VersionAdmin, admin.ModelAdmin):
   """ Admin handler for Department model """
      

class ProfessorAdmin(reversion.VersionAdmin, admin.ModelAdmin):
   """ Admin handler for Professor model """

admin.site.register(School)
admin.site.register(Professor)
admin.site.register(Course, CourseAdmin)
admin.site.register(ProfessorAffiliation)
