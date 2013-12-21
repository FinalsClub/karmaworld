#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
"""
"""

import datetime

from nose.tools import eq_
from nose.tools import ok_
from nose.tools import assert_is_none

from karmaworld.apps.notes.models import Note
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School


class BaseNote(object):
    def setup(self):
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
        self.note.save()

    def teardown(self):
        """ erase anything we created """
        print "generating a note teardown"
        self.note.delete()


class TestNoteWithRelation(BaseNote):
    """ Test the Note model with fkey to courses.models.Course """

    def test_unicode(self):
        """ Ensure that the unicode repl for a Note is as expected """
        expected = u"doc: Lecture notes concerning the use of therefore ∴ -- {0}"\
                .format(self.now)
        eq_(self.note.__unicode__(), expected)

    def test_course_fkey(self):
        eq_(self.course, self.note.course)


class TestNoteSlug(BaseNote):
    """ Test the conditional generation of the Note.slug field """

    expected = u'lecture-notes-concerning-the-use-of-therefore'

    def test_slug_natural(self):
        """ Test that the slug field is slugifying unicode Note.names """
        eq_(self.note.slug, self.expected)

    def test_remake_slug(self):
        """ Test the generation of a Note.slug field based on Note.name """
        self.note.slug = None
        self.note.save()
        eq_(self.note.slug, self.expected)

    def test_save_no_slug(self):
        """ Test that Note.save() doesn't make a slug
            if Note.name hasn't been set
        """
        self.note.name = None
        self.note.slug = None
        self.note.save() # re-save the note
        # check that slug has note been generated
        assert_is_none(self.note.slug)


class TestNoteUrl(BaseNote):
    expected_url_prefix = u'/marshall-college/archaeology-101/'
    expected_slug = u'lecture-notes-concerning-the-use-of-therefore'
    expected = expected_url_prefix + expected_slug

    def test_note_get_absolute_url_slug(self):
        """ Given a note with a slug, test that an expected url is generated """
        # check that Note.get_absolute_url() is generating the right url
        eq_(self.note.get_absolute_url(), self.expected)

    def test_note_get_absolute_url_id(self):
        self.note.slug = None
        url = self.expected_url_prefix + str(self.note.id)
        eq_(self.note.get_absolute_url(), url)
