from django.db import IntegrityError
from django.test import TestCase
from karmaworld.apps.courses.models import *
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.text import slugify
import json

class CoursesTests(TestCase):

    def setUp(self):
        self.harvard = School.objects.create(name="Harvard University")
        self.harvard.save()
        self.department = Department.objects.create(name="School of Study", school=self.harvard)
        self.department.save()
        self.course1 = Course.objects.create(name="Underwater Basketweaving", instructor_name="Alice Janney",
                                             school=self.harvard, department=self.department)
        self.client = Client()

    def testCourseUniqueness(self):
        """Make sure we can't create multiple courses with the same
        name + department name combination."""
        with self.assertRaises(IntegrityError):
            Course.objects.create(name=self.course1.name, instructor_name=self.course1.instructor_name,
                                  school=self.course1.school, department=self.department)
        self.assertEqual(Course.objects.count(), 1)

    def testSchoolSlug(self):
        self.assertEqual(self.harvard.slug, slugify(unicode(self.harvard.name)))

    def testCourseSlug(self):
        self.assertEqual(self.course1.slug, slugify(u"%s %s" % (self.course1.name, self.course1.id)))

    def testSearchForSchool(self):
        """Test searching for a school by partial name"""
        response = self.client.post(reverse('karmaworld.apps.courses.views.school_list'),
                                    {"q": "harvard u"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        responseContent = json.loads(response.content)

        # Did we get a good response back?
        self.assertIn('status', responseContent)
        self.assertEqual(responseContent['status'], 'success')
        self.assertIn('schools', responseContent)

        # Is the correct school in the list?
        self.assertEqual(responseContent['schools'][0]['name'], 'Harvard University')


    def testSearchForBadSchool(self):
        """Test searching for a school by partial name"""
        response = self.client.post(reverse('karmaworld.apps.courses.views.school_list'),
                                    {"q": "A FAKE SCHOOL"},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        responseContent = json.loads(response.content)

        self.assertIn('status', responseContent)
        self.assertEqual(responseContent['status'], 'success')
        self.assertEqual(len(responseContent['schools']), 0)


    def testSearchForCourseName(self):
        """Test searching for a school by partial name"""
        response = self.client.post(reverse('karmaworld.apps.courses.views.school_course_list'),
                                    {"q": "under", 'school_id': self.harvard.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        responseContent = json.loads(response.content)

        # Did we get a good response back?
        self.assertIn('status', responseContent)
        self.assertEqual(responseContent['status'], 'success')
        self.assertIn('courses', responseContent)

        # Is the correct school in the list?
        self.assertEqual(responseContent['courses'][0]['name'], 'Underwater Basketweaving')


    def testSearchForBadCourseName(self):
        """Test searching for a school by partial name"""
        response = self.client.post(reverse('karmaworld.apps.courses.views.school_course_list'),
                                    {"q": "A FAKE COURSE NAME", 'school_id': self.harvard.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        responseContent = json.loads(response.content)

        # Did we get a good response back?
        self.assertIn('status', responseContent)
        self.assertEqual(responseContent['status'], 'success')
        self.assertIn('courses', responseContent)

        # Is the correct school in the list?
        self.assertEqual(len(responseContent['courses']), 0)


    def testSearchForCourseNameWithBadRequest(self):
        """Test searching for a school by partial name"""
        response = self.client.post(reverse('karmaworld.apps.courses.views.school_course_list'),
                                    {"q": "under", 'school_id': '3737373737'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        responseContent = json.loads(response.content)

        # Did we get a good response back?
        self.assertIn('status', responseContent)
        self.assertEqual(responseContent['status'], 'fail')

    def testSearchForInstructorName(self):
        """Test searching for a school by partial name"""
        response = self.client.post(reverse('karmaworld.apps.courses.views.school_course_instructor_list'),
                                    {"q": "alice", 'course_name': self.course1.name, 'school_id': self.harvard.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        responseContent = json.loads(response.content)

        # Did we get a good response back?
        self.assertIn('status', responseContent)
        self.assertEqual(responseContent['status'], 'success')
        self.assertIn('instructors', responseContent)

        # Is the correct school in the list?
        self.assertEqual(responseContent['instructors'][0]['name'], 'Alice Janney')


    def testSearchForBadInstructorName(self):
        """Test searching for a school by partial name"""
        response = self.client.post(reverse('karmaworld.apps.courses.views.school_course_instructor_list'),
                                   {"q": "bob", 'course_name': self.course1.name, 'school_id': self.harvard.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        responseContent = json.loads(response.content)

        # Did we get a good response back?
        self.assertIn('status', responseContent)
        self.assertEqual(responseContent['status'], 'success')
        self.assertIn('instructors', responseContent)

        # Is the correct school in the list?
        self.assertEqual(len(responseContent['instructors']), 0)


    def testSearchForInstructorNameWithBadRequest(self):
        """Test searching for a school by partial name"""
        response = self.client.post(reverse('karmaworld.apps.courses.views.school_course_instructor_list'),
                                    {"q": "alice", 'course_name': self.course1.name, 'school_id': '3737373737'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        responseContent = json.loads(response.content)

        # Did we get a good response back?
        self.assertIn('status', responseContent)
        self.assertEqual(responseContent['status'], 'fail')



