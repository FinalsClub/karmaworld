#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
from django.contrib import admin
from karmaworld.apps.users.models import KarmaUser

admin.site.register(KarmaUser)