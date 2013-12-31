#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

from django.core.management.base import BaseCommand
from karmaworld.apps.notes.models import Note
from karmaworld.apps.notes.search import *

class Command(BaseCommand):
    args = 'none'
    help = "Populate the search index in IndexDen with all the notes" \
           "in the database. Will not clear the index beforehand, so notes" \
           "in the index that are not overwritten will still be around."

    def handle(self, *args, **kwargs):
        notes = Note.objects.all()

        for note in notes:
            try:
                print "Indexing {n}".format(n=note)
                add_document(note)
            except:
                continue

