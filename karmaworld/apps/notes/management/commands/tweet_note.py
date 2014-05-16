#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from django.core.management import BaseCommand
from karmaworld.apps.notes.tasks import tweet_note


class Command(BaseCommand):
    """ Tweet about a note that has recently been uploaded """
    args = 'none'
    help = "Send one tweet about a newly uploaded note."

    def handle(self, *args, **kwargs):
        tweet_note()
