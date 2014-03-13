#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from argparse import ArgumentError
from django.core.management import BaseCommand
from karmaworld.apps.quizzes.create_quiz import quiz_from_keywords


class Command(BaseCommand):
    args = '<note ID>'
    help = """
           Create a quiz out of the keywords and definitions
           already on file for the given note.
           """

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise ArgumentError("Incorrect arguments, see usage")
        quiz_from_keywords(args[0])

