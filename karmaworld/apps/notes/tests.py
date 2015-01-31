#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
import datetime
from django.test import TestCase
from karmaworld.apps.notes.search import SearchIndex

from karmaworld.apps.notes.models import Note, NoteMarkdown
from karmaworld.apps.notes import sanitizer
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School

class TestNotes(TestCase):

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
        self.note.uploaded_at = self.now
        self.note.text = "This is the plaintext version of a note. It's pretty cool. Alpaca."
        self.note.save()

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

    expected_url_prefix = u'/note/marshall-college/archaeology-101/'
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

    def test_note_markdown_rendering(self):
        rich = NoteMarkdown(note=self.note,
            markdown="""# This is fun\n[oh](http://yeah.com)""")
        rich.save()
        self.assertHTMLEqual(rich.html,
                """<h1>This is fun</h1>\n<p><a href="http://yeah.com" rel="nofollow" target="_blank">oh</a></p>""")

    def test_note_rich_text_sanitization(self):
        rich = NoteMarkdown(note=self.note, html="""
            <script>unsafe</script>
            <h1 class='obtrusive'>Something</h1>
            <h2>OK</h2>
            &amp;
            &rdquo;
            <a href='javascript:alert("Oh no")'>This stuff</a>
            <a href='http://google.com'>That guy</a>
        """)

        rich.save()
        self.assertHTMLEqual(rich.html, u"""
            <h1>Something</h1>
            <h2>OK</h2>
            &amp;
            \u201d
            <a>This stuff</a>
            <a href="http://google.com" target="_blank" rel="nofollow">That guy</a>
        """)

class TestSanitizer(TestCase):
    def test_clean(self):
        dirty = """
            <script>unsafe</script>
            <style>html {background-color: pink !important;}</style>
            <h1 class='obtrusive'>Something</h1>
            <h2>OK</h2>
            &amp;
            &rdquo;
            <a href='javascript:alert("Oh no")'>This stuff</a>
            <a href='http://google.com'>That guy</a>
            <section>
              <h3>This should show up</h3>
            </section>
        """

        self.assertHTMLEqual(sanitizer.sanitize_html(dirty), u"""
            <h1>Something</h1>
            <h2>OK</h2>
            &amp;
            \u201d
            <a>This stuff</a>
            <a href="http://google.com" target="_blank" rel="nofollow">That guy</a>
            <h3>This should show up</h3>
        """)

    def test_canonical_rel(self):
        html = """<h1>Hey there!</h1>"""
        canonicalized = sanitizer.set_canonical_rel(html, "http://example.com")
        self.assertHTMLEqual(canonicalized, """<html><head><link rel='canonical' href='http://example.com'></head><body><h1>Hey there!</h1></body></html>""")

    def test_data_uri(self):
        #html = '<img src="/this.gif">'
        #self.assertHTMLEqual(sanitizer.sanitize_html(html), "nothing")

        html = '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==">'
        self.assertHTMLEqual(sanitizer.sanitize_html(html), html)

        html = '<img src="data:application/pdf;base64,blergh">'
        self.assertHTMLEqual(sanitizer.sanitize_html(html), "<img/>")
