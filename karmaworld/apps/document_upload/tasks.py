#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

from celery.task import task
from karmaworld.apps.notes.gdrive import convert_with_google_drive

@task
def process_raw_document(raw_document):
    """ Process a RawDocument instance in to a Note instance """
    convert_raw_document(raw_document)

