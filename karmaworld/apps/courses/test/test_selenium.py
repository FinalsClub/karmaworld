import time
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

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(3)
        self.wait = WebDriverWait(self.driver, 200)
        self.harvard = School.objects.create(name="Harvard University", usde_id=12345)
        self.northeastern = School.objects.create(name="Northeastern University", usde_id=33333)

    def tearDown(self):
        self.driver.close()

    def select_autocomplete(self, name, keys):
        input = self.driver.find_element_by_name(name)
        input.send_keys(keys)
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//ul[contains(@style,'display: block')]/li[contains(@class,'ui-menu-item')][1]")))
        input.send_keys(Keys.DOWN)
        autocomplete_menu_item = self.driver.find_element_by_id("ui-active-menuitem")
        autocomplete_menu_item.click()

    def test_school_name(self):
        self.driver.get(self.live_server_url)

        # Click "Add Course"
        add_course_button = self.driver.find_element_by_id("add-course-btn")
        add_course_button.click()

        # Scroll down so the autocomplete menu is in view
        # This works around some weird failures
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Type in part of a school name
        school_input = self.driver.find_element_by_name("DepartmentForm-school_text")
        school_input.send_keys("harvard u")

        # Wait for autocomplete menu to appear
        # li.ui-menu-item:nth-child(1)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'ui-autocomplete')]/li[1]")))

        # Choose the first suggestion
        school_input.send_keys(Keys.DOWN)
        active_item = self.driver.find_element_by_id("ui-active-menuitem")
        active_item.click()

        school_name_on_deck = self.driver.find_element_by_xpath("//div[contains(@class,'results_on_deck')][1]")
        self.assertIn("Harvard University", school_name_on_deck.text)

        school_id = self.driver.find_element_by_name("DepartmentForm-school")
        self.assertEqual(school_id.get_attribute("value"), str(self.harvard.id))

    def test_create_course(self):
        self.driver.get(self.live_server_url)

        # Click "Add Course"
        add_course_button = self.driver.find_element_by_id("add-course-btn")
        add_course_button.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Choose a school
        self.select_autocomplete("DepartmentForm-school_text", "northeastern u")

        # Course name
        new_course_name = "SELENIUM TEST COURSE " + uuid.uuid4().hex
        course_name_input = self.driver.find_element_by_name("CourseForm-name")
        course_name_input.send_keys(new_course_name)

        # Department name
        new_department_name = "SELENIUM TEST DEPARTMENT " + uuid.uuid4().hex
        department_name_input = self.driver.find_element_by_name("DepartmentForm-name_text")
        department_name_input.send_keys(new_department_name)

        # Instructor name
        new_instructor_name = "SELENIUM TEST INSTRUCTOR " + uuid.uuid4().hex
        instructor_name_input = self.driver.find_element_by_name("ProfessorForm-name_text")
        instructor_name_input.send_keys(new_instructor_name)

        # Click "Save"
        save_button = self.driver.find_element_by_id("save-btn")
        save_button.click()

        # See if we are taken to the new course page
        self.wait.until(EC.title_contains(new_course_name))

    def test_create_existing_course(self):
        self.driver.get(self.live_server_url)

        # Click "Add Course"
        add_course_button = self.driver.find_element_by_id("add-course-btn")
        add_course_button.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Choose a school
        self.select_autocomplete("DepartmentForm-school_text", "northeastern u")

        # Course name
        new_course_name = "SELENIUM TEST COURSE " + uuid.uuid4().hex
        course_name_input = self.driver.find_element_by_name("CourseForm-name")
        course_name_input.send_keys(new_course_name)

        # Department name
        new_department_name = "SELENIUM TEST DEPARTMENT " + uuid.uuid4().hex
        department_name_input = self.driver.find_element_by_name("DepartmentForm-name_text")
        department_name_input.send_keys(new_department_name)

        # Instructor name
        new_instructor_name = "SELENIUM TEST INSTRUCTOR " + uuid.uuid4().hex
        instructor_name_input = self.driver.find_element_by_name("ProfessorForm-name_text")
        instructor_name_input.send_keys(new_instructor_name)

        # Click "Save"
        save_button = self.driver.find_element_by_id("save-btn")
        save_button.click()

        # See if we are taken to the new course page
        self.wait.until(EC.title_contains(new_course_name))

        # Now go back to the home page
        self.driver.get(self.live_server_url)

        # Click "Add Course"
        add_course_button = self.driver.find_element_by_id("add-course-btn")
        add_course_button.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Choose the SAME school
        self.select_autocomplete("DepartmentForm-school_text", "northeastern u")

        # The SAME course name
        self.select_autocomplete("CourseForm-name", new_course_name)

        # The SAME instructor name
        self.select_autocomplete("ProfessorForm-name_text", new_instructor_name)

        # The SAME department name
        self.select_autocomplete("DepartmentForm-name_text", new_department_name)

        save_button = self.driver.find_element_by_id("save-btn")
        save_button.click()
        self.assertEqual(Course.objects.count(), 1, "Duplicated course not created")

