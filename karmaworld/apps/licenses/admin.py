#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration configuration for notes """

from django.contrib import admin

from karmaworld.apps.licenses.models import License

admin.site.register(License)
