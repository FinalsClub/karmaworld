#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration configuration for notes """

from django.contrib import admin

from karmaworld.apps.notes import models


admin.site.register(models.DriveAuth)
admin.site.register(models.Note)
