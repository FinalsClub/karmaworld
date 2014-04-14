import itertools
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from django.test import LiveServerTestCase
from karmaworld.apps.courses.models import *
import new


class FieldAction:
    def __init__(self, field, value, autocomplete, error_expected, new_object_expected=True):
        self.field = field
        self.value = value
        self.autocomplete = autocomplete
        self.error_expected = error_expected
        self.new_object_expected = new_object_expected

    def __str__(self):
        return '{f}: "{v}"'.format(f=self.field, v=self.value)

    def __repr__(self):
        return str(self)


class CompositeFieldAction:
    def __init__(self, subactions, error_expected):
        self.subactions = subactions
        self.error_expected = error_expected

    def __str__(self):
        return str(self.subactions)

    def __repr__(self):
        return str(self)

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

SCHOOL_DEPARTMENT_FIELD_OPTIONS = (
    # Choose a school from autocomplete without department
    FieldAction(SCHOOL_FIELD_NAME, EXAMPLE_SCHOOL, autocomplete=True, error_expected=True),
    # Type in a school without choosing from autocomplete
    FieldAction(SCHOOL_FIELD_NAME, EXAMPLE_SCHOOL, autocomplete=False, error_expected=True),
    # Empty school name
    FieldAction(SCHOOL_FIELD_NAME, '', autocomplete=False, error_expected=True),

    # Choose school and type in new department
    CompositeFieldAction([
        FieldAction(SCHOOL_FIELD_NAME, EXAMPLE_SCHOOL, autocomplete=True, error_expected=False),
        FieldAction(DEPARTMENT_FIELD_NAME, EXAMPLE_NEW_DEPARTMENT, autocomplete=False, error_expected=False)],
                         error_expected=False),

    # Choose school and choose existing department
    CompositeFieldAction([
        FieldAction(SCHOOL_FIELD_NAME, EXAMPLE_SCHOOL, autocomplete=True, error_expected=False),
        FieldAction(DEPARTMENT_FIELD_NAME, EXAMPLE_EXISTING_DEPARTMENT, autocomplete=True, error_expected=False, new_object_expected=False)],
                         error_expected=False),
)

PROFESSOR_FIELDS_OPTIONS = (
    # New name and email typed in
    CompositeFieldAction([
        FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_NEW_PROFESSOR, autocomplete=False, error_expected=False),
        FieldAction(PROFESSOR_EMAIL_FIELD_NAME, EXAMPLE_NEW_PROFESSOR_EMAIL, autocomplete=False, error_expected=False)],
                         error_expected=False),
    # existing Professor Name selected, matching Professor Email selected
    CompositeFieldAction([
        FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR, autocomplete=True, error_expected=False, new_object_expected=False),
        FieldAction(PROFESSOR_EMAIL_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR_EMAIL, autocomplete=True, error_expected=False, new_object_expected=False)],
                         error_expected=False),
    # existing Professor Name selected, no Email selected
    CompositeFieldAction([
        FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR, autocomplete=True, error_expected=False, new_object_expected=False)],
                         error_expected=False),
    # existing Professor Email selected, no Name selected
    CompositeFieldAction([
        FieldAction(PROFESSOR_EMAIL_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR_EMAIL, autocomplete=True, error_expected=False, new_object_expected=False)],
                         error_expected=False),
    # existing Professor Name selected, different Professor Email selected
    CompositeFieldAction([
        FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_EXISTING_PROFESSOR, autocomplete=False, error_expected=False, new_object_expected=False),
        FieldAction(PROFESSOR_EMAIL_FIELD_NAME, EXAMPLE_NEW_PROFESSOR_EMAIL, autocomplete=False, error_expected=False, new_object_expected=False)],
                         error_expected=True),
)

COURSE_FIELDS_OPTIONS = (
    # new course name
    FieldAction(COURSE_FIELD_NAME, EXAMPLE_NEW_COURSE_NAME, autocomplete=False, error_expected=False),

    # new course name, with a URL
    CompositeFieldAction([
        FieldAction(COURSE_FIELD_NAME, EXAMPLE_NEW_COURSE_NAME, autocomplete=False, error_expected=False),
        FieldAction(COURSE_URL_FIELD_NAME, EXAMPLE_NEW_COURSE_URL, autocomplete=False, error_expected=False)],
                         error_expected=False),
    # empty course name
    FieldAction(COURSE_FIELD_NAME, '', autocomplete=False, error_expected=True),

    # empty course name, with a URL
    CompositeFieldAction([
        FieldAction(COURSE_FIELD_NAME, '', autocomplete=False, error_expected=True),
        FieldAction(COURSE_URL_FIELD_NAME, EXAMPLE_NEW_COURSE_URL, autocomplete=False, error_expected=False)],
                         error_expected=True),

)

HONEYPOT_FIELD_OPTIONS = (
    # something in the honeypot
    FieldAction(HONEYPOT_FIELD_NAME, EXAMPLE_HONEYPOT_VALUE, autocomplete=False, error_expected=True),
    # nothing in the honeypot
    FieldAction(HONEYPOT_FIELD_NAME, '', autocomplete=False, error_expected=False),
)

FIRST_AUTOCOMPLETE_XPATH = "//ul[contains(@style,'display: block')]/li[contains(@class,'ui-menu-item')][1]"


class DynamicTestCasesType(type):
    """Borrowed from
    http://stackoverflow.com/questions/347574/how-do-i-get-nose-to-discover-dynamically-generated-testcases"""
    def __new__(mcs, name, bases, dct):
        newdct = dct.copy()
        field_options_combinations = itertools.product(SCHOOL_DEPARTMENT_FIELD_OPTIONS,
                                                       PROFESSOR_FIELDS_OPTIONS,
                                                       COURSE_FIELDS_OPTIONS,
                                                       HONEYPOT_FIELD_OPTIONS)

        i = 0
        for actions in field_options_combinations:
            def m(self):
                self.do_actions(actions)

            test_name = "test_combination_{i}".format(i=i)
            m.func_name = test_name
            newdct[test_name] = new.function(m.func_code, globals(), test_name, tuple(), m.func_closure)
            i += 1

        return super(DynamicTestCasesType, mcs).__new__(mcs, name, bases, newdct)


class AddCourseTest(LiveServerTestCase):
    """Tests the Add Course form."""

    __metaclass__ = DynamicTestCasesType

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(3)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)
        super(AddCourseTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(AddCourseTest, cls).tearDownClass()

    def setUp(self):
        self.northeastern = School.objects.create(name=EXAMPLE_SCHOOL, usde_id=33333)
        self.department = Department.objects.create(name=EXAMPLE_EXISTING_DEPARTMENT, school=self.northeastern)
        self.professor = Professor.objects.create(name=EXAMPLE_EXISTING_PROFESSOR, email=EXAMPLE_EXISTING_PROFESSOR_EMAIL)
        self.course = Course.objects.create(name=EXAMPLE_EXISTING_COURSE_NAME, department=self.department)

    def tearDown(self):
        School.objects.all().delete()
        Department.objects.all().delete()
        Professor.objects.all().delete()
        Course.objects.all().delete()

    def select_autocomplete(self, name, keys):
        """Type in the characters into the given field, and then choose
        the first item in the autocomplete menu that appears."""
        input = self.driver.find_element_by_name(name)
        input.send_keys(keys)

        self.wait.until(EC.element_to_be_clickable((By.XPATH, FIRST_AUTOCOMPLETE_XPATH)))
        self.driver.find_element_by_xpath(FIRST_AUTOCOMPLETE_XPATH).click()

    @staticmethod
    def flatten_actions(actions):
        results = []
        for action in actions:
            if isinstance(action, CompositeFieldAction):
                results.extend(AddCourseTest.flatten_actions(action.subactions))
            else:
                results.append(action)

        return results

    def fill_out_form(self, field_actions):
        """Fill out the Add Course form with the given actions."""
        add_course_button = self.driver.find_element_by_id("add-course-btn")
        add_course_button.click()

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
            if isinstance(action, CompositeFieldAction) and \
                    (action.error_expected or self.expect_error(action.subactions)):
                result = True
            elif action.error_expected:
                result = True

        return result

    def check_object_exists(self, value, field, exists=True, actions=[]):
        desired_count = 1 if exists else 0

        if field == COURSE_FIELD_NAME:
            self.assertEqual(Course.objects.filter(name=value).count(), desired_count,
                             'Expected {n} courses with name "{name}" for actions {a}'.
                             format(n=desired_count, name=value, a=str(actions)))
        elif field == DEPARTMENT_FIELD_NAME:
            self.assertEqual(Department.objects.filter(name=value).count(), desired_count,
                             'Expected {n} departments with name "{name}" for actions {a}'.
                             format(n=desired_count, name=value, a=str(actions)))
        elif field == PROFESSOR_FIELD_NAME:
            self.assertEqual(Professor.objects.filter(name=value).count(), desired_count,
                             'Expected {n} professors with name "{name}" for actions {a}'.
                             format(n=desired_count, name=value, a=str(actions)))
        elif field == PROFESSOR_EMAIL_FIELD_NAME:
            self.assertEqual(Professor.objects.filter(email=value).count(), desired_count,
                             'Expected {n} professors with email "{email}" for actions {a}'.
                             format(n=desired_count, email=value, a=str(actions)))
        elif field == COURSE_URL_FIELD_NAME:
            self.assertEqual(Course.objects.filter(url=value).count(), desired_count,
                             'Expected {n} courses with url "{url}" for actions {a}'.
                             format(n=desired_count, url=value, a=str(actions)))

    def do_actions(self, actions):
        self.driver.get(self.live_server_url)
        error_expected = self.expect_error(actions)
        self.fill_out_form(actions)
        if error_expected:
            for action in AddCourseTest.flatten_actions(actions):
                if action.new_object_expected:
                    self.check_object_exists(action.value, action.field, exists=False, actions=actions)
        else:
            for action in AddCourseTest.flatten_actions(actions):
                if action.new_object_expected:
                    self.check_object_exists(action.value, action.field, exists=True, actions=actions)

    def test_duplicate_course_allowed(self):
        # A basic usage
        actions = [
            FieldAction(SCHOOL_FIELD_NAME, EXAMPLE_SCHOOL, autocomplete=True, error_expected=False),
            FieldAction(DEPARTMENT_FIELD_NAME, EXAMPLE_EXISTING_DEPARTMENT, autocomplete=True, error_expected=False),
            FieldAction(COURSE_FIELD_NAME, EXAMPLE_NEW_COURSE_NAME, autocomplete=False, error_expected=False),
            FieldAction(PROFESSOR_FIELD_NAME, EXAMPLE_NEW_PROFESSOR, autocomplete=False, error_expected=False),
        ]

        # Fill out field and make sure it worked
        self.do_actions(actions)
        for action in actions:
            self.check_object_exists(action.value, action.field, exists=True, actions=actions)

        # Fill out field again, and make sure duplicated were not created
        self.do_actions(actions)
        for action in actions:
            self.check_object_exists(action.value, action.field, exists=True, actions=actions)

