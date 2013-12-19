#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import magic
import re
import json
import time

import httplib2
from apiclient.discovery import build
from apiclient.http import MediaInMemoryUpload
from django.core.files.base import ContentFile
from oauth2client.client import SignedJwtAssertionCredentials

import secrets.drive as drive


PPT_MIMETYPES = ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']


def extract_file_details(fileobj):
    details = None
    year = None

    fileobj.open()
    filebuf = fileobj.read()
    with magic.Magic() as m:
        details = m.id_buffer(filebuf)
    fileobj.close()

    result = re.search(r'Create Time/Date:[^,]+(?P<year>\d{4})', details)
    if result:
        if 'year' in result.groupdict():
            year = result.groupdict()['year']

    return {'year': year}


def build_api_service():
    """
    Build and returns a Drive service object authorized with the service
    accounts that act on behalf of the given user.

    Will target the Google Drive of GOOGLE_USER email address.
    Returns a Google Drive service object.

    Code herein adapted from:
    https://developers.google.com/drive/delegation
    """

    # Extract the service address from the client secret
    with open(drive.CLIENT_SECRET, 'r') as fp:
        service_user = json.load(fp)['web']['client_email']

    # Pull in the service's p12 private key.
    with open(drive.SERVICE_KEY, 'rb') as p12:
        # Use the private key to auth as the service user for access to the
        # Google Drive of the GOOGLE_USER
        credentials = SignedJwtAssertionCredentials(service_user, p12.read(),
                               scope='https://www.googleapis.com/auth/drive',
                               sub=drive.GOOGLE_USER)

    return build('drive', 'v2', http=credentials.authorize(httplib2.Http()))


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
    else:
        download_urls['html'] = file_dict[u'exportLinks']['text/html']

    content_dict = {}
    for download_type, download_url in download_urls.items():
        print "\n%s -- %s" % (download_type, download_urls)
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
    while u'exportLinks' not in file_dict or
          u'text/plain' not in file_dict[u'exportLinks']:
        # wait some seconds
        print "upload_check_sleep({0})".format(2. ** delay_exp)
        time.sleep(2. ** delay_exp)
        delay_exp = delay_exp + 1

        # if 31.5 seconds have passed, give up
        if delay_exp == 5:
            raise ValueError('Google Drive failed to read the document.')

        # try to get the doc from gdrive
        file_dict = service.files().get(fileId=file_dict[u'id']).execute()

    return file_dict


def convert_raw_document(raw_document):
    """ Upload a raw document to google drive and get a Note back """
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

    # Include mimetype parameter if there is one to include
    extra_flags = {'mimetype': raw_document.mimetype} if raw_document.mimetype \
                  else {}
    media = MediaInMemoryUpload(fp_file.read(), chunksize=1024*1024, \
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

    if mimetype == 'application/pdf':
        note.file_type = 'pdf'

    elif mimetype in PPT_MIMETYPES:
        note.file_type = 'ppt'
        note.pdf_file.save(filename + '.pdf', ContentFile(content_dict['pdf']))

    elif 'html' in content_dict and content_dict['html']:
        note.html = content_dict['html']
        # before we save new html, sanitize a tags in note.html
        #note.sanitize_html(save=False)
        #FIXME: ^^^ disabled

    note.text = content_dict['text']

    note_details = extract_file_details(fp_file)
    if 'year' in note_details and note_details['year']:
        note.year = note_details['year']


    # Finally, save whatever data we got back from google
    note.save()
