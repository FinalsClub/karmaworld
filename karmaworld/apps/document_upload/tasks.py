#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import traceback

from celery import task
from celery.utils.log import get_task_logger
from karmaworld.apps.notes.gdrive import convert_raw_document

logger = get_task_logger(__name__)

@task()
def process_raw_document(raw_document, user):
    """ Process a RawDocument instance in to a Note instance """
    try:
        convert_raw_document(raw_document, user=user)
    except:
        logger.error(traceback.format_exc())

