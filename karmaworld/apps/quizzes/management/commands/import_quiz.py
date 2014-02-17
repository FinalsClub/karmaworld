#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from argparse import ArgumentError
from django.core.management import BaseCommand
from karmaworld.apps.quizzes.xml_import import quiz_from_xml, keywords_from_xml


class Command(BaseCommand):
    args = '<IQ-Metrics XML file> <note ID>'
    help = """
           Import a quiz from an IQ Metrics XML file
           """

    def handle(self, *args, **kwargs):
        if len(args) != 2:
            raise ArgumentError("Incorrect arguments, see usage")
        quiz_from_xml(args[0], args[1])
        keywords_from_xml(args[0], args[1])

