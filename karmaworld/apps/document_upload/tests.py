"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from karmaworld.apps.courses.models import Course
from karmaworld.apps.courses.models import School
from karmaworld.apps.document_upload.forms import RawDocumentForm
from karmaworld.apps.notes.gdrive import *
from karmaworld.apps.notes.models import Note, find_orphan_notes

TEST_USERNAME = 'alice'

class _FakeRequest:
    def __init__(self, session):
        self.session = session

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
        convert_raw_document(raw_document, user=user, session_key=session)
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
        """Test setting the user of an uploaded document to a known
        user in our database"""
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

    def testSessionUserAssociation2(self):
        """Test setting the user of an uploaded document
        to an existing user in the database, finding them
        through a session key."""
        user = User(username=TEST_USERNAME)
        user.save()
        s = SessionStore()
        s['_auth_user_id'] = user.pk
        s.save()
        self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/S2lhT3INSFCVFURR2RV7',
                                 'course': str(self.course.id),
                                 'name': 'graph3.txt',
                                 'tags': '',
                                 'mimetype': 'text/plain'},
                                 session=s)
        note = Note.objects.all()[0]
        self.assertEqual(note.user, user)



    def testSessionUserAssociation3(self):
        """Test setting the user of an uploaded document
        to an existing user in the database, finding them
        through a session key."""
        s = SessionStore()
        s.save()
        self.doConversionForPost({'fp_file': 'https://www.filepicker.io/api/file/S2lhT3INSFCVFURR2RV7',
                                 'course': str(self.course.id),
                                 'name': 'graph3.txt',
                                 'tags': '',
                                 'mimetype': 'text/plain'},
                                 session=s)
        user = User(username=TEST_USERNAME)
        user.save()

        # Normally this next bit is called automatically, but
        # in testing we need to call it manually
        note = Note.objects.all()[0]
        s = SessionStore(session_key=s.session_key)
        find_orphan_notes(note, user=user, request=_FakeRequest(s))

        note = Note.objects.all()[0]
        self.assertEqual(note.user, user)




