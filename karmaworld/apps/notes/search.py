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


class SearchResult(object):
    """The result of making a query into IndexDen.
    @param ordered_ids A list of the note IDs found, in order they
                       should be displayed
    @param snippet_dict A dictionary mapping note IDs to snippets
                        to show in search results
    @param has_more A boolean indicating if the user should
                    request more results by increasing
                    the page number of the query."""

    def __init__(self, ordered_ids, snippet_dict, has_more):
        self.ordered_ids = ordered_ids
        self.snippet_dict = snippet_dict
        self.has_more = has_more


class Singleton(type):
    """Set this as the metaclass of another
    class to ensure that it will only have one instance.
    Borrowed from
    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python"""

    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SearchIndex(object):
    """A singleton class used to interface with the IndexDen
    search index."""

    __metaclass__ = Singleton

    def __init__(self):
        api_client = itc.ApiClient(secret.PRIVATE_URL)
        if not api_client.get_index(secret.INDEX).exists():
            api_client.create_index(secret.INDEX, {'public_search': False})

        self.index = api_client.get_index(secret.INDEX)

        while not self.index.has_started():
            time.sleep(0.5)

        # Default scoring function
        # Results are sorted by combination of "relevance"
        # and number of thanks they have received.
        # "Relevance" is a black box provided by IndexDen.
        self.index.add_function(0, 'relevance * log(doc.var[0])')

    @staticmethod
    def _tags_to_str(tags):
        return ' '.join([str(tag) for tag in tags.all()])

    @staticmethod
    def _note_to_dict(note):
        d = {
            'name': note.name,
            'text': note.text
        }

        if note.tags.exists():
            d['tags'] = SearchIndex._tags_to_str(note.tags)

        if note.course:
            d['course_id'] = note.course.id

        if note.uploaded_at:
            d['timestamp'] = calendar.timegm(note.uploaded_at.timetuple())

        return d

    def add_note(self, note):
        """Add a note to the index. If the note is
        already in the index, it will be overwritten."""
        if note.text:
            logger.info("Indexing {n}".format(n=note))
            self.index.add_document(note.id, SearchIndex._note_to_dict(note), variables={0: note.thanks})
        else:
            logger.info("Note {n} has no text, will not add to IndexDen".format(n=note))

    def update_note(self, new_note, old_note):
        """Update a note. Will only truly update the search
        index if it needs to. Compares the fields in new_note with
        old_note to see what has changed."""
        if not new_note.text:
            logger.info("Note {n} has no text, will not add to IndexDen".format(n=new_note))
            return

        # If the indexable fields have changed,
        # send the document to IndexDen again
        if new_note.text != old_note.text or \
            new_note.name != old_note.name or \
            SearchIndex._tags_to_str(new_note.tags) != SearchIndex._tags_to_str(old_note.tags) or \
            new_note.course != old_note.course or \
            new_note.uploaded_at != old_note.uploaded_at:
            logger.info("Indexing {n}".format(n=new_note))
            self.index.add_document(new_note.id, SearchIndex._note_to_dict(new_note), variables={0: new_note.thanks})

        # If only the thanks count has changed, we can
        # just send that
        elif new_note.thanks != old_note.thanks:
            logger.info("Indexing thanks variable for {n}".format(n=new_note))
            self.index.update_variables(new_note.id, variables={0: new_note.thanks})

        # Otherwise we don't need to do anything
        else:
            logger.info("Note {n} has not changed sufficiently, will not update IndexDen".format(n=new_note))

    def remove_note(self, note):
        """Remove a note from the search index."""

        logger.info("Removing from index: {n}".format(n=note))
        self.index.delete_document(note.id)

    def search(self, query, course_id=None, page=0):
        """Returns an instance of SearchResult for your query."""

        if course_id:
            real_query = '("%s" OR name:"%s") AND course_id:%s' % (query, query, course_id)
        else:
            real_query = '"%s" OR name:"%s"' % (query, query)

        raw_results = self.index.search(real_query, snippet_fields=['text'],
                                   length=PAGE_SIZE, start=(page*PAGE_SIZE))

        ordered_ids = [int(r['docid']) for r in raw_results['results']]
        snippet_dict = {int(r['docid']): r['snippet_text'] for r in raw_results['results']}

        # Are there more results to show the user if they want?
        has_more = True if int(raw_results['matches']) > ((page+1) * PAGE_SIZE) else False

        return SearchResult(ordered_ids, snippet_dict, has_more)
