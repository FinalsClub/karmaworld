#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
import time
import json

from django.conf import settings
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

            if note.static_html:
                # grab the html from inside the note and process it
                html_resp = requests.get('http:{0}{1}'.format(settings.S3_URL, note.get_relative_s3_path()))
                if html_resp.status_code is not 200:
                    print html_resp.text
                    continue
                html = html_resp.text
            else:
                html = note.html

            fp_policy_json = '{{"expiry": {0}, "call": ["pick","store","read","stat"]}}'
            fp_policy_json = fp_policy_json.format(int(time.time() + 31536000))
            fp_policy      = encode_fp_policy(fp_policy_json)
            fp_signature   = sign_fp_policy(fp_policy)

            upload_resp = requests.post('https://www.filepicker.io/api/store/S3',
                          params={'key': FILEPICKER_API_KEY,
                                  'policy': fp_policy,
                                  'signature': fp_signature,
                                  'filename': slugify(note.name)},
                          headers={'Content-Type': 'text/html; charset=utf-8'},
                          data=html.encode('utf-8'))

            if upload_resp.status_code is not 200:
                print upload_resp.text
                continue

            resp_json = json.loads(upload_resp.text)
            url = resp_json['url']
            note.fp_file = url

            get_resp = requests.get(url,
                                    params={'key': FILEPICKER_API_KEY,
                                            'policy': fp_policy,
                                            'signature': fp_signature})

            if get_resp.status_code is not 200:
                print "It looks like this note upload did not succeed"
                print str(note)
                continue

            if get_resp.text != html:
                print "The content at the new Filepicker URL does not match the original note contents!"

            note.save()


