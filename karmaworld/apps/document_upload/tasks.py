#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

from celery import task
from karmaworld.apps.notes.gdrive import convert_raw_document

@task()
def process_raw_document(raw_document):
    """ Process a RawDocument instance in to a Note instance """
    print "="*80
    print "this line should be deferred and only printed by celery"
    convert_raw_document(raw_document)

