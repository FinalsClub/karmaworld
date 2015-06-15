#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
import base64

import datetime
import logging
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from karmaworld.apps.notes.models import UserUploadMapping
from karmaworld.apps.notes.models import NoteMarkdown
from karmaworld.apps.notes import sanitizer
from karmaworld.apps.quizzes.models import Keyword
from karmaworld.apps.users.models import NoteKarmaEvent
import os
import subprocess
import tempfile
import uuid
import magic
import re
import json
import time

import httplib2
import html2text
from apiclient.discovery import build
from apiclient.http import MediaInMemoryUpload
from oauth2client.client import SignedJwtAssertionCredentials

logger = logging.getLogger(__name__)

PDF_MIMETYPE = 'application/pdf'
PPT_MIMETYPES = ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']

GOOGLE_SERVICE_EMAIL = os.environ['GOOGLE_SERVICE_EMAIL']
GOOGLE_SERVICE_KEY_BASE64 = os.environ['GOOGLE_SERVICE_KEY_BASE64']
GOOGLE_USER = os.environ['GOOGLE_USER']

def build_api_service():
    """
    Build and returns a Drive service object authorized with the service
    accounts that act on behalf of the given user.

    Will target the Google Drive of GOOGLE_USER email address.
    Returns a Google Drive service object.

    Code herein adapted from:
    https://developers.google.com/drive/delegation
    """

    # Pull in the service's p12 private key.
    p12 = base64.decodestring(GOOGLE_SERVICE_KEY_BASE64)
    credentials = SignedJwtAssertionCredentials(GOOGLE_SERVICE_EMAIL, p12,
                               scope='https://www.googleapis.com/auth/drive',
                               sub=GOOGLE_USER)

    return build('drive', 'v2', http=credentials.authorize(httplib2.Http()))


def pdf2html(content):
    pdf_file = tempfile.NamedTemporaryFile()
    pdf_file.write(content)
    pdf_file.flush()
    tmp_dir = tempfile.gettempdir()
    html_file_name = uuid.uuid4().hex
    html_file_path = os.path.join(tmp_dir, html_file_name)

    command = ['pdf2htmlEX', pdf_file.name, html_file_name]
    devnull = open('/dev/null', 'w')
    if settings.TESTING:
        call = subprocess.Popen(command, shell=False, cwd=tmp_dir, stdout=devnull, stderr=devnull)
    else:
        call = subprocess.Popen(command, shell=False, cwd=tmp_dir)
    call.wait()
    devnull.close()
    if call.returncode != 0:
        raise ValueError("PDF file could not be processed")

    pdf_file.close()

    try:
        html_file = open(html_file_path, 'r')
        html = html_file.read()
        html_file.close()
        os.remove(html_file_path)
    except IOError, e:
        raise ValueError("PDF file could not be processed")

    if len(html) == 0:
        raise ValueError("PDF file results in empty HTML file")

    return html


def download_from_gdrive(service, file_dict, extension=None, mimetype=None):
    """ Take in a gdrive service, file_dict from upload, and either an
        extension or mimetype.
        You must provide an `extension` or `mimetype`
        Returns contextual files from google
    """
    download_urls = {}
    download_urls['text'] = file_dict[u'exportLinks']['text/plain']

    if extension:
        extension = extension.lower()

    if extension in ['.ppt', 'pptx'] \
        or mimetype in PPT_MIMETYPES:
        download_urls['pdf'] = file_dict[u'exportLinks']['application/pdf']
    elif mimetype == PDF_MIMETYPE:
        pass
    else:
        download_urls['html'] = file_dict[u'exportLinks']['text/html']

    content_dict = {}
    for download_type, download_url in download_urls.items():
        print "\n%s -- %s" % (download_type, download_url)
        resp, content = service._http.request(download_url)

        if resp.status in [200]:
            print "\t downloaded!"
            # save to the File.property resulting field
            content_dict[download_type] = content
        else:
            print "\t Download failed: %s" % resp.status

    return content_dict


def upload_to_gdrive(service, media, filename, extension=None, mimetype=None):
    """ take a gdrive service object, and a media wrapper and upload to gdrive
        returns a file_dict
        You must provide an `extension` or `mimetype`
    """
    _resource = {'title': filename}

    # clean up extensions for type checking
    if extension:
        extension = extension.lower()

    # perform OCR on files that are image intensive
    ocr = extension in ['.pdf', '.jpeg', '.jpg', '.png'] or \
          mimetype in ['application/pdf']

    file_dict = service.files().insert(body=_resource, media_body=media,\
                                       convert=True, ocr=ocr).execute()

    # increase exponent of 2 for exponential growth.
    # 2 ** -1 = 0.5, 2 ** 0 = 1, 2 ** 1 = 2, 4, 8, 16, ...
    delay_exp = -1
    # exponentially wait for exportLinks to be returned if missing
    while u'exportLinks' not in file_dict or \
          u'text/plain' not in file_dict[u'exportLinks']:
        # if a bunch  seconds have passed, give up
        if delay_exp == 7:
            raise ValueError('Google Drive failed to read the document.')

        # wait some seconds
        print "upload_check_sleep({0})".format(2. ** delay_exp)
        time.sleep(2. ** delay_exp)
        delay_exp = delay_exp + 1

        # try to get the doc from gdrive
        file_dict = service.files().get(fileId=file_dict[u'id']).execute()

    return file_dict


def convert_raw_document(raw_document, user=None):
    """ Upload a raw document to google drive and get a Note back"""
    fp_file = raw_document.get_file()

    # extract some properties from the document metadata
    filename = raw_document.name
    print "this is the mimetype of the document to check:"
    mimetype = raw_document.mimetype
    print mimetype
    print ""

    # A special case for Evernotes
    if raw_document.mimetype == 'text/enml':
        raw_document.mimetype = 'text/html'

    original_content = fp_file.read()

    # Include mimetype parameter if there is one to include
    extra_flags = {'mimetype': raw_document.mimetype} if raw_document.mimetype \
                  else {}
    media = MediaInMemoryUpload(original_content, chunksize=1024*1024, \
                                resumable=True, **extra_flags)


    service = build_api_service()

    # upload to google drive
    file_dict = upload_to_gdrive(service, media, filename, mimetype=mimetype)

    # download from google drive
    content_dict = download_from_gdrive(service, file_dict, mimetype=mimetype)

    # this should have already happened, lets see why it hasn't
    raw_document.is_processed = True
    raw_document.save()

    note = raw_document.convert_to_note()

    # Cache the uploaded file's URL
    note.gdrive_url = file_dict['alternateLink']
    note.text = content_dict['text']

    # Extract HTML from the appropriate place
    html = ''
    if raw_document.mimetype == PDF_MIMETYPE:
        html = pdf2html(original_content)
    elif raw_document.mimetype in PPT_MIMETYPES:
        html = pdf2html(content_dict['pdf'])
    elif 'html' in content_dict and content_dict['html']:
        html = content_dict['html']

    if html:
        html = sanitizer.data_uris_to_s3(html)
        NoteMarkdown.objects.create(note=note, html=html)

    # If we know the user who uploaded this,
    # associate them with the note
    if user and not user.is_anonymous():
        note.user = user
        NoteKarmaEvent.create_event(user, note, NoteKarmaEvent.UPLOAD)
    else:
        try:
            mapping = UserUploadMapping.objects.get(fp_file=raw_document.fp_file)
            note.user = mapping.user
            note.save()
            NoteKarmaEvent.create_event(mapping.user, note, NoteKarmaEvent.UPLOAD)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            logger.info("Zero or multiple mappings found with fp_file " + raw_document.fp_file.name)

    # Finally, save whatever data we got back from google
    note.save()





