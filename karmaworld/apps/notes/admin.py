#!/usr/bin/python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" Administration configuration for notes """

from django.contrib import admin

import models

admin.site.register(models.Note)
