#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from django.core.management import BaseCommand
from karmaworld.apps.quizzes.xml_import import quiz_from_xml


class Command(BaseCommand):
    help = """
           Import a quiz from an IQ Metrics XML file
           """

    def handle(self, *args, **kwargs):
        quiz_from_xml(args[0])


