#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

import datetime

from django.http import HttpResponse
from karmaworld.apps.document_upload.forms import RawDocumentForm
from karmaworld.apps.notes.models import ANONYMOUS_UPLOAD_URLS


def save_fp_upload(request):
    """ ajax endpoint for saving a FilePicker uploaded file form
    """
    r_d_f = RawDocumentForm(request.POST)

    if r_d_f.is_valid():
        raw_document = r_d_f.save(commit=False)

        raw_document.fp_file = request.POST['fp_file']

        raw_document.ip = request.META['REMOTE_ADDR']
        raw_document.uploaded_at = datetime.datetime.utcnow()

        if request.user.is_authenticated():
            raw_document.save()
        else:
            anonymous_upload_urls = request.session.get(ANONYMOUS_UPLOAD_URLS, [])
            anonymous_upload_urls.append(request.POST['fp_file'])
            request.session[ANONYMOUS_UPLOAD_URLS] = anonymous_upload_urls
            request.session.modified = True
            request.session.save()
            raw_document.save()
        # save the tags to the database, too. don't forget those guys.
        r_d_f.save_m2m()
        # Proccess document after the tags are saved so that it isn't converted
        # to a note before the tags are attached to the document
        raw_document.process_document(user=request.user)

        return HttpResponse({'success'})
    else:
        return HttpResponse(r_d_f.errors, status=400)
