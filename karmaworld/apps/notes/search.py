#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import calendar
import time

import indextank.client as itc
import karmaworld.secret.indexden as secret

import logging

PAGE_SIZE = 10

logging.basicConfig()
logger = logging.getLogger(__name__)

api_client = itc.ApiClient(secret.PRIVATE_URL)
if not api_client.get_index(secret.INDEX).exists():
    api_client.create_index(secret.INDEX, {'public_search': False})

index = api_client.get_index(secret.INDEX)

while not index.has_started():
    time.sleep(0.5)

# Default scoring function
# Results are sorted by combination of "relevance"
# and number of thanks they have received.
# "Relevance" is a black box provided by IndexDen.
index.add_function(0, 'relevance * log(doc.var[0])')

class SearchResult(object):

    def __init__(self, ordered_ids, snippet_dict, has_more):
        self.ordered_ids = ordered_ids
        self.snippet_dict = snippet_dict
        self.has_more = has_more

def note_to_dict(note):
    d = {
        'name': note.name,
        'text': note.text
    }

    if note.tags.exists():
        d['tags'] = ' '.join([str(tag) for tag in note.tags.all()])

    if note.course:
        d['course_id'] = note.course.id

    if note.uploaded_at:
        d['timestamp'] = calendar.timegm(note.uploaded_at.timetuple())

    return d

def add_document(note):
    if note.text:
        index.add_document(note.id, note_to_dict(note), variables={0: note.thanks})
    else:
        logger.warn("Note {n} has no text, will not add to IndexDen".format(n=note))

def remove_document(note):
    index.delete_document(note.id)

def search(query, course_id=None, page=0):
    """Returns note IDs matching the given query,
    filtered by course ID if given"""
    if course_id:
        real_query = '("%s" OR name:"%s") AND course_id:%s' % (query, query, course_id)
    else:
        real_query = '"%s" OR name:"%s"' % (query, query)

    raw_results = index.search(real_query, snippet_fields=['text'],
                               length=PAGE_SIZE, start=(page*PAGE_SIZE))

    ordered_ids = [int(r['docid']) for r in raw_results['results']]
    snippet_dict = {int(r['docid']): r['snippet_text'] for r in raw_results['results']}

    # Are there more results to show the user if they want?
    has_more = True if int(raw_results['matches']) > ((page+1) * PAGE_SIZE) else False

    return SearchResult(ordered_ids, snippet_dict, has_more)
