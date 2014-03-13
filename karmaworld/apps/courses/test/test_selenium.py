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
        self.wait = WebDriverWait(self.driver, 10)
        self.harvard = School.objects.create(name="Harvard University", usde_id=12345)
        self.northeastern = School.objects.create(name="Northeastern University", usde_id=33333)

    def tearDown(self):
        self.driver.close()

    def selectAutocomplete(self, name, keys, fieldIndex):
        input = self.driver.find_element_by_name(name)
        input.send_keys(keys)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'ui-autocomplete')]/li[" + str(fieldIndex) + "]")))
        input.send_keys(Keys.DOWN)
        autocompleteMenuItem = self.driver.find_element_by_id("ui-active-menuitem")
        autocompleteMenuItem.click()

    def testSchoolName(self):
        self.driver.get(self.live_server_url)

        # Click "Add Course"
        addCourseButton = self.driver.find_element_by_id("add-course-btn")
        addCourseButton.click()

        # Scroll down so the autocomplete menu is in view
        # This works around some weird failures
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Type in part of a school name
        schoolInput = self.driver.find_element_by_name("DepartmentForm-school_text")
        schoolInput.send_keys("harvard u")

        # Wait for autocomplete menu to appear
        # li.ui-menu-item:nth-child(1)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'ui-autocomplete')]/li[1]")))

        # Choose the first suggestion
        schoolInput.send_keys(Keys.DOWN)
        activeItem = self.driver.find_element_by_id("ui-active-menuitem")
        activeItem.click()

        school_name_on_deck = self.driver.find_element_by_xpath("//div[contains(@class,'results-on-deck')][1]")
        self.assertIn("Harvard University", school_name_on_deck.text)

        schoolId = self.driver.find_element_by_name("DepartmentForm-school")
        self.assertEqual(schoolId.get_attribute("value"), str(self.harvard.id))

    def testCreateCourse(self):
        self.driver.get(self.live_server_url)

        # Click "Add Course"
        addCourseButton = self.driver.find_element_by_id("add-course-btn")
        addCourseButton.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Choose a school
        self.selectAutocomplete("DepartmentForm-school_text", "northeastern u", 1)

        # Course name
        newCourseName = "SELENIUM TEST COURSE " + uuid.uuid4().hex
        courseNameInput = self.driver.find_element_by_id("id_CourseForm-name")
        courseNameInput.send_keys(newCourseName)

        # Instructor name
        newInstructorName = "SELENIUM TEST INSTRUCTOR " + uuid.uuid4().hex
        instructorNameInput = self.driver.find_element_by_id("id_ProfessorForm-name_text")
        instructorNameInput.send_keys(newInstructorName)

        # Click "Save"
        saveButton = self.driver.find_element_by_id("save-btn")
        saveButton.click()

        # See if we are taken to the new course page
        self.wait.until(EC.title_contains(newCourseName))


    def testCreateExistingCourse(self):
        self.driver.get(self.live_server_url)

        # Click "Add Course"
        addCourseButton = self.driver.find_element_by_id("add-course-btn")
        addCourseButton.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Choose a school
        self.selectAutocomplete("DepartmentForm-school_text", "northeastern u", 1)

        # Course name
        newCourseName = "SELENIUM TEST COURSE " + uuid.uuid4().hex
        courseNameInput = self.driver.find_element_by_id("id_CourseForm-name")
        courseNameInput.send_keys(newCourseName)

        # Instructor name
        newInstructorName = "SELENIUM TEST INSTRUCTOR " + uuid.uuid4().hex
        instructorNameInput = self.driver.find_element_by_id("id_ProfessorForm-name_text")
        instructorNameInput.send_keys(newInstructorName)

        # Click "Save"
        saveButton = self.driver.find_element_by_id("save-btn")
        saveButton.click()

        # See if we are taken to the new course page
        self.wait.until(EC.title_contains(newCourseName))

        # Now go back to the home page
        self.driver.get(self.live_server_url)

        # Click "Add Course"
        addCourseButton = self.driver.find_element_by_id("add-course-btn")
        addCourseButton.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Choose the SAME school
        self.selectAutocomplete("DepartmentForm-school_text", "northeastern u", 1)

        # The SAME course name
        self.selectAutocomplete("id_CourseForm-name", newCourseName, 2)

        # The SAME instructor name
        self.selectAutocomplete("id_ProfessorForm-name_text", newInstructorName, 3)

        saveButton.click()



