"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest

from django.test import TestCase, Client
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School
from karmaworld.apps.document_upload.forms import RawDocumentForm
from karmaworld.apps.notes.gdrive import *
from karmaworld.apps.notes.models import Note, ANONYMOUS_UPLOAD_URLS
from karmaworld.apps.notes.models import find_orphan_notes

TEST_USERNAME = 'alice'


class ConversionTest(TestCase):

    def setUp(self):
        self.school = School(name='Northeastern University')
        self.school.save()
        self.course = Course(name='Intro to Advanced Study', school=self.school)
        self.course.save()
        self.client = Client()

    def doConversionForPost(self, post, user=None, session=None):
        self.assertEqual(Note.objects.count(), 0)
        r_d_f = RawDocumentForm(post)
        self.assertTrue(r_d_f.is_valid())
        raw_document = r_d_f.save(commit=False)
        raw_document.fp_file = post['fp_file']
        convert_raw_document(raw_document, user=user)
        self.assertEqual(Note.objects.count(), 1)

    def testPlaintextConversion(self):
        """Test upload of a plain text file"""
        self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/S2lhT3INSFCVFURR2RV7',
                                 'course': str(self.course.id),
                                 'name': 'graph3.txt',
                                 'tags': '',
                                 'mimetype': 'text/plain'})

    def testEvernoteConversion(self):
        """Test upload of an Evernote note"""
        self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/vOtEo0FrSbu2WDbAOzLn',
                                 'course': str(self.course.id),
                                 'name': 'KarmaNotes test 3',
                                 'tags': '',
                                 'mimetype': 'text/enml'})

    def testPdfConversion(self):
        """Test upload of a PDF"""
        self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/8l6mtMURnu1uXvcvJo9s',
                                 'course': str(self.course.id),
                                 'name': 'geneve_1564.pdf',
                                 'tags': '',
                                 'mimetype': 'application/pdf'})

    def testGarbage(self):
        """Test upload of a file with a bogus mimetype"""
        with self.assertRaises(ValueError):
            self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/H85Xl8VURqiGusxhZKMl',
                                     'course': str(self.course.id),
                                     'name': 'random',
                                     'tags': '',
                                     'mimetype': 'application/octet-stream'})

    def testSessionUserAssociation1(self):
        """If the user is already logged in when they
        upload a note, it should set note.user correctly."""
        user = User(username=TEST_USERNAME)
        user.save()
        self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/S2lhT3INSFCVFURR2RV7',
                                 'course': str(self.course.id),
                                 'name': 'graph3.txt',
                                 'tags': '',
                                 'mimetype': 'text/plain'},
                                 user=user)
        note = Note.objects.all()[0]
        self.assertEqual(note.user, user)
        try:
            NoteKarmaEvent.objects.get(note=note, event_type=NoteKarmaEvent.UPLOAD)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")

    def testSessionUserAssociation2(self):
        """If a user logs in after convert_raw_document has finished,
        we should associate them with the note they uploaded anonymously"""
        s = SessionStore()
        s[ANONYMOUS_UPLOAD_URLS] = ['https://www.filepicker.io/api/file/S2lhT3INSFCVFURR2RV7']
        s.save()
        self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/S2lhT3INSFCVFURR2RV7',
                                 'course': str(self.course.id),
                                 'name': 'graph3.txt',
                                 'tags': '',
                                 'mimetype': 'text/plain'})
        user = User(username=TEST_USERNAME)
        user.save()
        request = HttpRequest()
        request.session = s
        find_orphan_notes(None, user=user, request=request)
        note = Note.objects.all()[0]
        self.assertEqual(note.user, user)
        try:
            NoteKarmaEvent.objects.get(note=note, event_type=NoteKarmaEvent.UPLOAD)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")

    def testSessionUserAssociation3(self):
        """If a user logs in WHILE convert_raw_document is running,
        make sure they are associated with that note by the time it finishes."""
        s = SessionStore()
        s[ANONYMOUS_UPLOAD_URLS] = ['https://www.filepicker.io/api/file/S2lhT3INSFCVFURR2RV7']
        s.save()
        user = User(username=TEST_USERNAME)
        user.save()
        request = HttpRequest()
        request.session = s
        find_orphan_notes(None, user=user, request=request)
        self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/S2lhT3INSFCVFURR2RV7',
                                 'course': str(self.course.id),
                                 'name': 'graph3.txt',
                                 'tags': '',
                                 'mimetype': 'text/plain'},
                                 session=s)
        note = Note.objects.all()[0]
        self.assertEqual(note.user, user)
        try:
            NoteKarmaEvent.objects.get(note=note, event_type=NoteKarmaEvent.UPLOAD)
        except ObjectDoesNotExist:
            self.fail("Karma event not created")
