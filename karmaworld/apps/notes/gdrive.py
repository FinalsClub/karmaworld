#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

import datetime
from io import FileIO, BufferedWriter
import mimetypes
import os
import time

import httplib2
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from django.conf import settings
from django.core.files import File
from oauth2client.client import flow_from_clientsecrets

from karmaworld.apps.notes.models import DriveAuth, Note

CLIENT_SECRET = os.path.join(settings.DJANGO_ROOT, \
                    'secret/client_secrets.json')
#from credentials import GOOGLE_USER # FIXME
try:
    from secrets.drive import GOOGLE_USER
except:
    GOOGLE_USER = 'admin@karmanotes.org' # FIXME

EXT_TO_MIME = {'.docx': 'application/msword'}

def build_flow():
    """ Create an oauth2 autentication object with our preferred details """
    scopes = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
    ]

    flow = flow_from_clientsecrets(CLIENT_SECRET, ' '.join(scopes), \
            redirect_uri='http://localhost:8000/oauth2callback')
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    flow.params['user_id'] = GOOGLE_USER
    return flow


def authorize():
    """ Use an oauth2client flow object to generate the web url to create a new
        auth that can be then stored """
    flow = build_flow()
    print flow.step1_get_authorize_url()


def accept_auth(code):
    """ Callback endpoint for accepting the post `authorize()` google drive
        response, and generate a credentials object
        :code:  An authentication token from a WEB oauth dialog
        returns a oauth2client credentials object """
    flow = build_flow()
    creds = flow.step2_exchange(code)
    return creds


def build_api_service(creds):
    http = httplib2.Http()
    http = creds.authorize(http)
    return build('drive', 'v2', http=http), http


def check_and_refresh(creds, auth):
    """ Check a Credentials object's expiration token
        if it is out of date, refresh the token and save
        :creds: a Credentials object
        :auth:  a DriveAuth that backs the cred object
        :returns: updated creds and auth objects
    """
    if creds.token_expiry < datetime.datetime.utcnow():
        # if we are passed the token expiry,
        # refresh the creds and store them
        http = httplib2.Http()
        http = creds.authorize(http)
        creds.refresh(http)
        auth.credentials = creds.to_json()
        auth.save()
    return creds, auth

def download_from_gdrive(file_dict, http, extension):
    """ get urls from file_dict and download contextual files from google """
    download_urls = {}
    download_urls['text'] = file_dict[u'exportLinks']['text/plain']
    if extension.lower() in ['.ppt', 'pptx']:
        download_urls['pdf'] = file_dict[u'exportLinks']['application/pdf']
    else:
        download_urls['html'] = file_dict[u'exportLinks']['text/html']


    content_dict = {}
    for download_type, download_url in download_urls.items():
        print "\n%s -- %s" % (download_type, download_urls)
        resp, content = http.request(download_url, "GET")

        if resp.status in [200]:
            print "\t downloaded!"
            # save to the File.property resulting field
            content_dict[download_type] = content
        else:
            print "\t Download failed: %s" % resp.status

    return content_dict

def upload_to_gdrive(service, media, filename, extension):
    """ take a gdrive service object, and a media wrapper and upload to gdrive
        returns a file_dict """
    _resource = {'title': filename}
    if extension.lower() in ['.pdf', '.jpeg', '.jpg', '.png']:
        # include OCR on ocr-able files
        file_dict = service.files().insert(body=_resource, media_body=media, convert=True, ocr=True).execute()

    else:
        file_dict = service.files().insert(body=_resource, media_body=media, convert=True).execute()

    if u'exportLinks' not in file_dict:
        # wait some seconds
        # get the doc from gdrive
        time.sleep(30)
        file_dict = service.files().get(fileId=file_dict[u'id']).execute()

    return file_dict

def convert_with_google_drive(note):
    """ Upload a local note and download HTML
        using Google Drive
        :note: a File model instance # FIXME
    """
    # TODO: set the permission of the file to permissive so we can use the
    #       gdrive_url to serve files directly to users

    # Get file_type and encoding of uploaded file
    # i.e: file_type = 'text/plain', encoding = None
    (file_type, encoding) = mimetypes.guess_type(note.note_file.path)



    if file_type != None:
        media = MediaFileUpload(note.note_file.path, mimetype=file_type,
                    chunksize=1024*1024, resumable=True)

    else:
        media = MediaFileUpload(note.note_file.path,
                    chunksize=1024*1024, resumable=True)

    auth = DriveAuth.objects.filter(email=GOOGLE_USER).all()[0]
    creds = auth.transform_to_cred()


    creds, auth = check_and_refresh(creds, auth)

    service, http = build_api_service(creds)

    # get the file extension
    filename, extension = os.path.splitext(note.note_file.path)

    file_dict = upload_to_gdrive(service, media, filename, extension)

    content_dict = download_from_gdrive(file_dict, http, extension)


    # Get a new copy of the file from the database with the new metadata from filemeta
    new_note = Note.objects.get(id=note.id)
    if extension.lower() == '.pdf':
        new_note.file_type = 'pdf'

    elif extension.lower() in ['.ppt', '.pptx']:
        print "try to save ppt"
        now = datetime.datetime.utcnow()
        # create a folder path to store the ppt > pdf file with year and month folders
        _path = os.path.join(settings.MEDIA_ROOT, 'ppt_pdf/%s/%s' % (now.year, now.month), filename)
        try:
            # If those folders don't exist, create them
            os.makedirs(os.path.realpath(os.path.dirname(_path)))

        _writer = BufferedWriter(FileIO(_path, "w"))
        _writer.write(content_dict['pdf'])
        _writer.close()


        new_note.pdf_file = os.path.join(_path, filename)

    # set the .odt as the download from google link
    if extension.lower() in ['.ppt', '.pptx']:
        print "is ppt"
        new_note.pdf_file = File(content_dict['pdf'])
    else:
        # PPT files do not have this export ability
        new_note.gdrive_url = file_dict[u'exportLinks']['application/vnd.oasis.opendocument.text']
        new_note.html = content_dict['html']

    new_note.text = content_dict['text']

    # before we save new html, sanitize a tags in note.html
    new_note.sanitize_html(save=False)

    # Finally, save whatever data we got back from google
    new_note.save()
