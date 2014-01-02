#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

import datetime

from django.http import HttpResponse
from karmaworld.apps.document_upload.forms import RawDocumentForm
from karmaworld.apps.users.models import KarmaUser


def save_fp_upload(request):
    """ ajax endpoint for saving a FilePicker uploaded file form
    """
    r_d_f = RawDocumentForm(request.POST)
    if r_d_f.is_valid():
        raw_document = r_d_f.save(commit=False)

        print request.POST.keys()
        time_a = datetime.datetime.now()
        raw_document.fp_file = request.POST['fp_file']

        time_b = datetime.datetime.now()
        delta = time_b - time_a
        raw_document.ip = request.META['REMOTE_ADDR']
        raw_document.uploaded_at = datetime.datetime.utcnow()
        if request.POST['email'] != '':
            raw_document.user = KarmaUser.objects.get_or_create(email=request.POST['email'])[0]
        time_c = datetime.datetime.now()
        # note that .save() has the side-effect of kicking of a celery processing task
        raw_document.save()
        # save the tags to the database, too. don't forget those guys.
        r_d_f.save_m2m()
        time_d = datetime.datetime.now()
        delta = time_d - time_c
        print "d\t%s" % delta
        return HttpResponse({'success'})
    else:
        return HttpResponse(r_d_f.errors, status=400)
