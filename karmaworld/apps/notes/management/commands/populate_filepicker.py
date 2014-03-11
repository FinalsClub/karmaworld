#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
import time
import json

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from karmaworld.apps.notes.models import Note
from karmaworld.utils.filepicker import sign_fp_policy, encode_fp_policy
import requests
from karmaworld.secret.filepicker import FILEPICKER_API_KEY


class Command(BaseCommand):
    args = 'none'
    help = """
           For each note that does not have a fp_file properly
           populated, upload its HTML contents to Filepicker and
           set fp_file.
           """

    def handle(self, *args, **kwargs):
        for note in Note.objects.iterator():
            if note.fp_file.name:
                print "Skipping {0}".format(str(note))
                continue

            # grab the html from inside the note and process it
            html = note.filter_html(note.html)

            fp_policy_json = '{{"expiry": {0}, "call": ["pick","store","read","stat"]}}'
            fp_policy_json = fp_policy_json.format(int(time.time() + 31536000))
            fp_policy      = encode_fp_policy(fp_policy_json)
            fp_signature   = sign_fp_policy(fp_policy)

            resp = requests.post('https://www.filepicker.io/api/store/S3',
                          params={'key': FILEPICKER_API_KEY,
                                  'policy': fp_policy,
                                  'signature': fp_signature,
                                  'filename': slugify(note.name)})

            if resp.status_code is not 200:
                print resp.text
                continue

            resp_json = json.loads(resp.text)
            note.fp_file = resp_json['url']
            note.save()


