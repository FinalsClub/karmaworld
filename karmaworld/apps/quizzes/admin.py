#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from django.contrib import admin
from karmaworld.apps.quizzes.models import Keyword, KeywordExtractionHIT, EmailParsingHIT

admin.site.register(Keyword)
admin.site.register(KeywordExtractionHIT)
admin.site.register(EmailParsingHIT)
