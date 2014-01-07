#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration configuration for notes """

from django.contrib import admin

from karmaworld.apps.schools.models import School
from karmaworld.apps.schools.models import Department

admin.site.register(School)
admin.site.register(Department)
