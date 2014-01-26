#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import datetime
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.test import TestCase

from django.contrib.auth.models import User
from karmaworld.apps.courses.views import flag_course
from karmaworld.apps.notes.models import Note
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School
from karmaworld.apps.notes.search import SearchIndex
from karmaworld.apps.notes.views import thank_note, flag_note, downloaded_note
from karmaworld.apps.users.models import NoteKarmaEvent, GenericKarmaEvent, CourseKarmaEvent, give_email_confirm_karma


class TestUsers(TestCase):

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

        self.user1 = User(username='Alice')
        self.user1.save()

        self.user2 = User(username='Bob')
        self.user2.save()

        # create a note to test against
        self.note = Note()
        self.note.course = self.course
        self.note.name = u"Lecture notes concerning the use of therefore ∴"
        self.note.text = "This is the plaintext version of a note. It's pretty cool."
        self.note.user = self.user1
        self.note.save()

        self.request1 = HttpRequest()
        self.request1.user = self.user1
        self.request1.method = 'POST'
        self.request1.META = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        self.request1.session = SessionStore()

        self.request2 = HttpRequest()
        self.request2.user = self.user2
        self.request2.method = 'POST'
        self.request2.META = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        self.request2.session = SessionStore()

    @classmethod
    def setUpClass(cls):
        index = SearchIndex(testing=True)
        index.setup(testing=True)

    @classmethod
    def tearDownClass(cls):
        """Delete the test index that was automatically
        created by notes/search.py"""
        index = SearchIndex()
        index.delete_index()

    def test_thank_own_note_karma(self):
        """Make sure you don't get karma for thanking your own note"""
        thank_note(self.request1, self.note.pk)
        try:
            NoteKarmaEvent.objects.get(note=self.note)
            self.fail("You can't thank your own note")
        except ObjectDoesNotExist:
            pass

    def test_thank_anothers_note_karma(self):
        """Get karma for having your note thanked"""
        thank_note(self.request2, self.note.pk)
        try:
            NoteKarmaEvent.objects.get(note=self.note)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")

    def test_note_deleted_karma(self):
        """Lose karma if your note is deleted"""
        thank_note(self.request2, self.note.pk)
        self.note.delete()
        try:
            GenericKarmaEvent.objects.get(event_type=GenericKarmaEvent.NOTE_DELETED)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")
        try:
            NoteKarmaEvent.objects.get(note=self.note)
            self.fail("Karma event not deleted")
        except ObjectDoesNotExist:
            pass

    def test_note_give_flag_karma(self):
        """Lose karma for flagging a note"""
        flag_note(self.request2, self.note.pk)
        try:
            NoteKarmaEvent.objects.get(event_type=NoteKarmaEvent.GIVE_FLAG, user=self.user2)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")

    def test_course_give_flag_karma(self):
        """Lose karma for flagging a course"""
        flag_course(self.request2, self.course.pk)
        try:
            CourseKarmaEvent.objects.get(event_type=CourseKarmaEvent.GIVE_FLAG, user=self.user2)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")

    def test_note_get_flagged_karma(self):
        """Lose karma for having your note flagged many times"""
        flag_note(self.request2, self.note.pk)
        flag_note(self.request2, self.note.pk)
        flag_note(self.request2, self.note.pk)
        flag_note(self.request2, self.note.pk)
        flag_note(self.request2, self.note.pk)
        flag_note(self.request2, self.note.pk)
        try:
            NoteKarmaEvent.objects.get(event_type=NoteKarmaEvent.GET_FLAGGED, user=self.user1)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")

    def test_note_download_karma(self):
        """You lose karma for downloading a note, person who uploaded it gains karma"""
        downloaded_note(self.request2, self.note.pk)
        try:
            NoteKarmaEvent.objects.get(event_type=NoteKarmaEvent.DOWNLOADED_NOTE, user=self.user2)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")
        try:
            NoteKarmaEvent.objects.get(event_type=NoteKarmaEvent.HAD_NOTE_DOWNLOADED, user=self.user1)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")

    def test_email_confirm_karma(self):
        class FakeEmailAddress:
            user = self.user1
            email = self.user1.email

        give_email_confirm_karma(None, email_address=FakeEmailAddress())
        try:
            GenericKarmaEvent.objects.get(event_type=GenericKarmaEvent.EMAIL_CONFIRMED, user=self.user1)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")
