#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation

from django.conf import settings

def s3_url(request):
    return { 'S3_URL': settings.S3_URL }


