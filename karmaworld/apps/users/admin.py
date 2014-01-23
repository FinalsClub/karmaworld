#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
from django.contrib import admin
from karmaworld.apps.users.models import UserProfile, NoteKarmaEvent, CourseKarmaEvent, GenericKarmaEvent


admin.site.register(UserProfile)
admin.site.register(GenericKarmaEvent)
admin.site.register(NoteKarmaEvent)
admin.site.register(CourseKarmaEvent)
