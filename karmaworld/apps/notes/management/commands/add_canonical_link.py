#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from karmaworld.apps.notes.models import Note
from karmaworld.secret.static_s3 import S3_URL
import requests


class Command(BaseCommand):
    help = """
           Add a <link rel='canonical' ... /> to every note stored in S3
           """

    def handle(self, *args, **kwargs):
        for note in Note.objects.all():
            note_path = 'http:' + S3_URL + note.get_relative_s3_path()
            resp = requests.get(note_path)
            if resp.status_code != 200:
                print("Could not retrieve " + note_path)
                continue
            html = resp.text

            soup = BeautifulSoup(html)
            soup = note.set_canonical_link(soup)

            note.update_note_on_s3(unicode(soup))
            print("Updated note " + unicode(note))

