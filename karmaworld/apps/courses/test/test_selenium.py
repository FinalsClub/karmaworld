import itertools
from nose import with_setup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from django.test import LiveServerTestCase
from karmaworld.apps.courses.models import *
import uuid


class AddCourseTest(LiveServerTestCase):
    """Tests the Add Course form."""

    class FieldAction:
        def __init__(self, field, value, autocomplete, error_expected):
            self.field = field
            self.value = value
            self.autocomplete = autocomplete
            self.error_expected = error_expected

        def __str__(self):
            return "{f}: {v}".format(f=self.field, v=self.value)

    class CompositeFieldAction:
        def __init__(self, subactions, error_expected):
            self.subactions = subactions
            self.error_expected = error_expected

    SCHOOL_FIELD_NAME = 'DepartmentForm-school_text'
    COURSE_FIELD_NAME = 'CourseForm-name'
    DEPARTMENT_FIELD_NAME = 'DepartmentForm-name_text'
    PROFESSOR_FIELD_NAME = 'ProfessorForm-name_text'
    PROFESSOR_EMAIL_FIELD_NAME = 'ProfessorForm-email_text'
    COURSE_URL_FIELD_NAME = 'CourseForm-url'
    HONEYPOT_FIELD_NAME = 'CourseForm-instruction_url'

    EXAMPLE_SCHOOL = 'Northeastern University'
    EXAMPLE_NEW_DEPARTMENT = 'College of Arts and Sciences'
    EXAMPLE_EXISTING_DEPARTMENT = 'College of Computer and Information Sciences'
    EXAMPLE_NEW_PROFESSOR = 'Prof. X'
    EXAMPLE_NEW_PROFESSOR_EMAIL = 'xavier@xmen.edu'
    EXAMPLE_EXISTING_PROFESSOR = 'Prof. Einstein'
    EXAMPLE_EXISTING_PROFESSOR_EMAIL = 'einstein@princeton.edu'
    EXAMPLE_NEW_COURSE_NAME = 'Algorithms and Data'
    EXAMPLE_EXISTING_COURSE_NAME = 'Theory of Computation'
    EXAMPLE_NEW_COURSE_URL = 'http://neu.edu/stuff'
    EXAMPLE_HONEYPOT_VALUE = 'Free drugs!'

    SCHOOL_FIELD_OPTIONS = (
        # Choose a school from autocomplete
        FieldAction(SCHOOL_FIELD_NAME, EXAMPLE_SCHOOL, autocomplete=True, error_expected=False),
        # Type in a school without choosing from autocomplete
        FieldAction(SCHOOL_FIELD_NAME, EXAMPLE_SCHOOL, autocomplete=False, error_expected=True),
        # Empty school name
        FieldAction(SCHOOL_FIELD_NAME, '', autocomplete=False, error_expected=True)
    )

    DEPARTMENT_FIELD_OPTIONS = (
        # Type in a new department
        FieldAction(DEPARTMENT_FIELD_NAME, EXAMPLE_NEW_DEPARTMENT, autocomplete=False, error_expected=False),
        # Choose an existing department
        FieldAction(DEPARTMENT_FIELD_NAME, EXAMPLE_EXISTING_DEPARTMENT, autocomplete=True, error_expected=False)
    )

    PROFESSOR_FIELDS_OPTIONS = (
        # New name and email typed in
        CompositeFieldAction([
            FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_NEW_PROFESSOR, autocomplete=False, error_expected=False),
            FieldAction(PROFESSOR_EMAIL_FIELD_NAME, EXAMPLE_NEW_PROFESSOR_EMAIL, autocomplete=False, error_expected=False)],
                             error_expected=False),
        # existing Professor Name selected, matching Professor Email selected
        CompositeFieldAction([
            FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR, autocomplete=True, error_expected=False),
            FieldAction(PROFESSOR_EMAIL_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR_EMAIL, autocomplete=True, error_expected=False)],
                             error_expected=False),
        # existing Professor Name selected, no Email selected
        CompositeFieldAction([
            FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR, autocomplete=True, error_expected=False)],
                             error_expected=False),
        # existing Professor Email selected, no Name selected
        CompositeFieldAction([
            FieldAction(PROFESSOR_EMAIL_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR_EMAIL, autocomplete=True, error_expected=False)],
                             error_expected=False),
        # existing Professor Name selected, different Professor Email selected
        CompositeFieldAction([
            FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR, autocomplete=False, error_expected=False),
            FieldAction(PROFESSOR_EMAIL_FIELD_NAME, EXAMPLE_NEW_PROFESSOR_EMAIL, autocomplete=False, error_expected=False)],
                             error_expected=True),
    )

    COURSE_FIELD_OPTIONS = (
        # new course name
        FieldAction(COURSE_FIELD_NAME, EXAMPLE_NEW_COURSE_NAME, autocomplete=False, error_expected=False),
        # empty course name
        FieldAction(COURSE_FIELD_NAME, '', autocomplete=False, error_expected=True)
    )

    COURSE_URL_OPTIONS = (
        # no URL
        FieldAction(COURSE_URL_FIELD_NAME, '', autocomplete=False, error_expected=False),
        # URL given
        FieldAction(COURSE_URL_FIELD_NAME, EXAMPLE_NEW_COURSE_URL, autocomplete=False, error_expected=False)
    )

    HONEYPOT_FIELD_OPTIONS = (
        # something in the honeypot
        FieldAction(HONEYPOT_FIELD_NAME, EXAMPLE_HONEYPOT_VALUE, autocomplete=False, error_expected=True),
        # nothing in the honeypot
        FieldAction(HONEYPOT_FIELD_NAME, '', autocomplete=False, error_expected=False)
    )

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(3)
        cls.wait = WebDriverWait(cls.driver, 200)
        super(AddCourseTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(AddCourseTest, cls).tearDownClass()

    def set_up(self):
        self.northeastern = School.objects.create(name=self.EXAMPLE_SCHOOL, usde_id=33333)
        self.department = Department.objects.create(name=self.EXAMPLE_EXISTING_DEPARTMENT, school=self.northeastern)
        self.professor = Professor.objects.create(name=self.EXAMPLE_EXISTING_PROFESSOR, email=self.EXAMPLE_EXISTING_PROFESSOR_EMAIL)
        self.course = Course.objects.create(name=self.EXAMPLE_EXISTING_COURSE_NAME, department=self.department)

    def tear_down(self):
        School.objects.all().delete()
        Department.objects.all().delete()
        Professor.objects.all().delete()
        Course.objects.all().delete()

    def select_autocomplete(self, name, keys):
        """Type in the characters into the given field, and then choose
        the first item in the autocomplete menu that appears."""
        input = self.driver.find_element_by_name(name)
        input.send_keys(keys)
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//ul[contains(@style,'display: block')]/li[contains(@class,'ui-menu-item')][1]")))
        input.send_keys(Keys.DOWN)
        autocomplete_menu_item = self.driver.find_element_by_id("ui-active-menuitem")
        autocomplete_menu_item.click()

    @staticmethod
    def flatten_actions(actions):
        results = []
        for action in actions:
            if isinstance(action, AddCourseTest.CompositeFieldAction):
                results.extend(AddCourseTest.flatten_actions(action.subactions))
            else:
                results.append(action)

        return results

    def fill_out_form(self, field_actions):
        """Fill out the Add Course form with the given actions."""
        add_course_button = self.driver.find_element_by_id("add-course-btn")
        add_course_button.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        for action in AddCourseTest.flatten_actions(field_actions):
            if action.autocomplete:
                self.select_autocomplete(action.field, action.value)
            else:
                field = self.driver.find_element_by_name(action.field)
                field.send_keys(action.value)

        # Click "Save"
        save_button = self.driver.find_element_by_id("save-btn")
        save_button.click()

    def expect_error(self, actions):
        result = False
        for action in actions:
            if isinstance(action, AddCourseTest.CompositeFieldAction) and \
                    self.expect_error(action.subactions):
                result = True
            elif action.error_expected:
                result = True

        return result

    def check_object_exists(self, value, field, exists=True):
        desired_count = 1 if exists else 0

        if field == self.COURSE_FIELD_NAME:
            self.assertEqual(Course.objects.filter(name=value).count(), desired_count)
        elif field == self.DEPARTMENT_FIELD_NAME:
            self.assertEqual(Department.objects.filter(name=value).count(), desired_count)
        elif field == self.PROFESSOR_FIELD_NAME:
            self.assertEqual(Professor.objects.filter(name=value).count(), desired_count)
        elif field == self.PROFESSOR_EMAIL_FIELD_NAME:
            self.assertEqual(Professor.objects.filter(email=value).count(), desired_count)
        elif field == self.COURSE_URL_FIELD_NAME:
            self.assertEqual(Course.objects.filter(url=value).count(), desired_count)

    def actions_test_and_check(self, actions):
        self.set_up()
        self.driver.get(self.live_server_url)
        error_expected = self.expect_error(actions)
        self.fill_out_form(actions)
        if error_expected:
            for action in AddCourseTest.flatten_actions(actions):
                self.check_object_exists(action.value, action.field, exists=False)
        else:
            for action in AddCourseTest.flatten_actions(actions):
                self.check_object_exists(action.value, action.field, exists=True)
        self.tear_down()

    def test_combinations(self):
        field_options_combinations = itertools.product(self.SCHOOL_FIELD_OPTIONS,
                                                       self.DEPARTMENT_FIELD_OPTIONS,
                                                       self.PROFESSOR_FIELDS_OPTIONS,
                                                       self.COURSE_FIELD_OPTIONS,
                                                       self.COURSE_URL_OPTIONS,
                                                       self.HONEYPOT_FIELD_OPTIONS)

        for actions in field_options_combinations:
            self.actions_test_and_check(actions)
