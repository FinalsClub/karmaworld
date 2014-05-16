#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
from django.contrib import admin
import csv
import StringIO
from django.contrib.admin import ModelAdmin
from django.http import HttpResponse
from karmaworld.apps.users.models import UserProfile, NoteKarmaEvent, CourseKarmaEvent, GenericKarmaEvent

def user_export(modeladmin, request, queryset):
    f = StringIO.StringIO()
    writer = csv.writer(f, dialect='excel')
    writer.writerow(['First Name', 'Last Name', 'Email'])
    for user_profile in queryset:
        user = user_profile.user
        writer.writerow([user.first_name, user.last_name, user.email])
    return HttpResponse(f.getvalue())
user_export.short_description = "Download a CSV file with users' information"


class UserProfileAdmin(ModelAdmin):
    actions = (user_export,)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(GenericKarmaEvent)
admin.site.register(NoteKarmaEvent)
admin.site.register(CourseKarmaEvent)
