#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
"""
"""
import karmaworld.secret.indexden as secret
import uuid

# This needs to happen before other things
# are imported to avoid putting test data
# in our production search index
secret.INDEX = uuid.uuid4().hex

import datetime
from django.test import TestCase
from karmaworld.apps.notes.search import SearchIndex

from karmaworld.apps.notes.models import Note
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School
import indextank.client as itc

class TestNoes(TestCase):

    def setUp(self):
        # create base values to test db representations
        self.now = datetime.datetime.utcnow()

        # create a school to satisfy course requirements
        self.school = School()
        self.school.name = 'Marshall College'
        self.school.save()

        # create a course to test relationships
        self.course = Course()
        self.course.school = self.school
        self.course.name = u'Archaeology 101'
        self.course.save()
        # override Course.save() appending an ID to the slug
        self.course.slug = u'archaeology-101'
        self.course.save()

        # create a note to test against
        self.note = Note()
        self.note.course = self.course
        self.note.name = u"Lecture notes concerning the use of therefore ∴"
        #self.note.slug := do not set for test_remake_slug() behavior
        self.note.file_type = 'doc'
        self.note.uploaded_at = self.now
        self.note.text = "This is the plaintext version of a note. It's pretty cool. Alpaca."
        self.note.save()

    @classmethod
    def tearDownClass(cls):
        """Delete the test index that was automatically
        created by notes/search.py"""
        api = itc.ApiClient(secret.PRIVATE_URL)
        api.delete_index(secret.INDEX)

    def test_course_fkey(self):
        self.assertEqual(self.course, self.note.course)

    def test_slug_natural(self):
        """ Test that the slug field is slugifying unicode Note.names """
        expected = u"lecture-notes-concerning-the-use-of-therefore"
        self.assertEqual(self.note.slug, expected)

    def test_remake_slug(self):
        """ Test the generation of a Note.slug field based on Note.
        Name collision is expected, so see if slug handles this."""
        expected = u"lecture-notes-concerning-the-use-of-therefore-{0}-{1}-{2}".format(
                    self.note.uploaded_at.month,
                    self.note.uploaded_at.day, self.note.uploaded_at.microsecond)

        self.note.slug = None
        self.note.save()
        self.assertEqual(self.note.slug, expected)

    expected_url_prefix = u'/marshall-college/archaeology-101/'
    expected_slug = u'lecture-notes-concerning-the-use-of-therefore'
    expected = expected_url_prefix + expected_slug

    def test_note_get_absolute_url_slug(self):
        """ Given a note with a slug, test that an expected url is generated """
        # check that Note.get_absolute_url() is generating the right url
        self.assertEqual(self.note.get_absolute_url(), self.expected)

    def test_note_get_absolute_url_id(self):
        self.note.slug = None
        url = self.expected_url_prefix + str(self.note.id)
        self.assertEqual(self.note.get_absolute_url(), url)

    def test_search_index(self):
        """Search for a note within IndexDen"""

        index = SearchIndex()

        # Search for it
        results = index.search('alpaca')
        self.assertIn(self.note.id, results.ordered_ids)

        # Search for it, filtering by course
        results = index.search('alpaca', self.note.course.id)
        self.assertIn(self.note.id, results.ordered_ids)


