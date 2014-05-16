#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from django.core.management import BaseCommand
from karmaworld.apps.quizzes.tasks import get_extract_keywords_results


class Command(BaseCommand):
    """ Download results from Mechanical Turk """
    args = 'none'
    help = "Download results from Mechanical Turk."

    def handle(self, *args, **kwargs):
        get_extract_keywords_results()
