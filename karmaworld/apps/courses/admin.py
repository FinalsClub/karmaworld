#!/usr/bin/python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration configuration for courses """

from django.contrib import admin

import models

admin.site.register(models.School)
admin.site.register(models.Course)
