#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseForbidden
from karmaworld.apps.quizzes.models import Keyword
from karmaworld.utils import ajax_base


def set_keyword(annotation_uri, keyword, definition, ranges):
    try:
        keyword = Keyword.objects.get(note_id=annotation_uri, word=keyword, ranges=ranges)
        keyword.definition = definition
        keyword.save()
    except ObjectDoesNotExist:
        Keyword.objects.create(note_id=annotation_uri, word=keyword, definition=definition, ranges=ranges)


def delete_keyword(annotation_uri, keyword, definition, ranges):
    keyword = Keyword.objects.get(note_id=annotation_uri, word=keyword, definition=definition, ranges=ranges)
    keyword.definition = definition
    keyword.delete()


def process_set_delete_keyword(request):
    annotator_data = json.loads(request.raw_post_data)
    annotation_uri = annotator_data['uri']
    keyword = annotator_data['quote']
    definition = annotator_data['text']
    ranges = json.dumps(annotator_data['ranges'])

    if not request.user.is_authenticated():
        return HttpResponseForbidden(json.dumps({'status': 'fail', 'message': "Only authenticated users may set keywords"}),
                                     mimetype="application/json")

    try:
        if request.method in ('POST', 'PUT'):
            set_keyword(annotation_uri, keyword, definition, ranges)
        elif request.method == 'DELETE':
            delete_keyword(annotation_uri, keyword, definition, ranges)
    except Exception, e:
        return HttpResponseNotFound(json.dumps({'status': 'fail', 'message': e.message}),
                                    mimetype="application/json")


def set_delete_keyword_annotator(request):
    return ajax_base(request, process_set_delete_keyword, ('POST', 'PUT', 'DELETE'))


def get_keywords_annotator(request):
    annotation_uri = request.GET['uri']

    try:
        keywords = Keyword.objects.filter(note_id=annotation_uri).exclude(ranges=None)
        keywords_data = {
            'total': len(keywords),
            'rows': []
        }
        for keyword in keywords:
            keyword_data = {
                'quote': keyword.word,
                'text': keyword.definition,
                'ranges': json.loads(keyword.ranges),
                'created': keyword.timestamp.isoformat(),
            }
            keywords_data['rows'].append(keyword_data)

        return HttpResponse(json.dumps(keywords_data), mimetype='application/json')

    except ObjectDoesNotExist, e:
        return HttpResponseNotFound(json.dumps({'status': 'fail', 'message': e.message}),
                                    mimetype="application/json")


def get_keywords_datatables(request):
    annotation_uri = request.GET['uri']

    try:
        keywords = Keyword.objects.filter(note_id=annotation_uri)
        keywords_data = {
            'total': len(keywords),
            'rows': []
        }
        for keyword in keywords:
            keyword_data = {
                'quote': keyword.word,
                'text': keyword.definition,
                'ranges': json.loads(keyword.ranges),
                'created': keyword.timestamp.isoformat(),
            }
            keywords_data['rows'].append(keyword_data)

        return HttpResponse(json.dumps(keywords_data), mimetype='application/json')

    except ObjectDoesNotExist, e:
        return HttpResponseNotFound(json.dumps({'status': 'fail', 'message': e.message}),
                                    mimetype="application/json")

