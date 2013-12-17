from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import uuid
import unittest


class AddCourseTest(unittest.TestCase):
    """Tests the Add Course form. Requires a copy of KarmaNotes
    be available at localhost:8000. This will modify your database."""

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(3)
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.close()

    def selectAutocomplete(self, inputId, keys, fieldIndex):
        input = self.driver.find_element_by_id(inputId)
        input.send_keys(keys)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'ui-autocomplete')][" + str(fieldIndex) + "]/li")))
        input.send_keys(Keys.DOWN)
        autocompleteMenuItem = self.driver.find_element_by_id("ui-active-menuitem")
        autocompleteMenuItem.click()

    def testSchoolName(self):
        self.driver.get("http://localhost:8000/")

        # Click "Add Course"
        addCourseButton = self.driver.find_element_by_id("add-course-btn")
        addCourseButton.click()

        # Scroll down so the autocomplete menu is in view
        # This works around some weird failures
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Type in part of a school name
        schoolInput = self.driver.find_element_by_id("str_school")
        schoolInput.send_keys("harvard u")

        # Wait for autocomplete menu to appear
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'ui-autocomplete')][1]/li")))

        # Choose the first suggestion
        schoolInput.send_keys(Keys.DOWN)
        activeItem = self.driver.find_element_by_id("ui-active-menuitem")
        activeItem.click()

        self.assertEqual(schoolInput.get_attribute("value"), "Harvard University")

        schoolId = self.driver.find_element_by_id("id_school")
        self.assertEqual(schoolId.get_attribute("value"), "1817")

    def testCreateCourse(self):
        self.driver.get("http://localhost:8000/")

        # Click "Add Course"
        addCourseButton = self.driver.find_element_by_id("add-course-btn")
        addCourseButton.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # We shouldn't be able to save it yet
        saveButton = self.driver.find_element_by_id("save-btn")
        self.assertIn("disabled", saveButton.get_attribute("class"))

        # Choose a school
        self.selectAutocomplete("str_school", "northeastern u", 1)

        # Check that save button is now enabled
        self.assertNotIn("disabled", saveButton.get_attribute("class"))

        # Course name
        newCourseName = "SELENIUM TEST COURSE " + uuid.uuid4().hex
        courseNameInput = self.driver.find_element_by_id("id_name")
        courseNameInput.send_keys(newCourseName)

        # Instructor name
        newInstructorName = "SELENIUM TEST INSTRUCTOR " + uuid.uuid4().hex
        instructorNameInput = self.driver.find_element_by_id("id_instructor_name")
        instructorNameInput.send_keys(newInstructorName)

        # Click "Save"
        saveButton = self.driver.find_element_by_id("save-btn")
        saveButton.click()

        # See if we are taken to the new course page
        self.wait.until(EC.title_contains(newCourseName))


    def testCreateExistingCourse(self):
        self.driver.get("http://localhost:8000/")

        # Click "Add Course"
        addCourseButton = self.driver.find_element_by_id("add-course-btn")
        addCourseButton.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # We shouldn't be able to save it yet
        saveButton = self.driver.find_element_by_id("save-btn")
        self.assertIn("disabled", saveButton.get_attribute("class"))

        # Choose a school
        self.selectAutocomplete("str_school", "northeastern u", 1)

        # Check that save button is now enabled
        self.assertNotIn("disabled", saveButton.get_attribute("class"))

        # Course name
        newCourseName = "SELENIUM TEST COURSE " + uuid.uuid4().hex
        courseNameInput = self.driver.find_element_by_id("id_name")
        courseNameInput.send_keys(newCourseName)

        # Instructor name
        newInstructorName = "SELENIUM TEST INSTRUCTOR " + uuid.uuid4().hex
        instructorNameInput = self.driver.find_element_by_id("id_instructor_name")
        instructorNameInput.send_keys(newInstructorName)

        # Click "Save"
        saveButton = self.driver.find_element_by_id("save-btn")
        saveButton.click()

        # See if we are taken to the new course page
        self.wait.until(EC.title_contains(newCourseName))

        # Now go back to the home page
        self.driver.get("http://localhost:8000/")

        # Click "Add Course"
        addCourseButton = self.driver.find_element_by_id("add-course-btn")
        addCourseButton.click()
        self.driver.execute_script("javascript:window.scrollBy(0,200)")

        # Choose the SAME school
        self.selectAutocomplete("str_school", "northeastern u", 1)

        # The SAME course name
        self.selectAutocomplete("id_name", newCourseName, 2)

        # The SAME instructor name
        self.selectAutocomplete("id_instructor_name", newInstructorName, 3)

        # Make sure Save button is disabled and hidden
        saveButton = self.driver.find_element_by_id("save-btn")
        self.assertIn("disabled", saveButton.get_attribute("class"))
        self.wait.until_not(EC.visibility_of(saveButton))

        # Make sure Existing Course link is shown
        existingCourse = self.driver.find_element_by_id("existing-course-btn")
        self.wait.until(EC.visibility_of(existingCourse))
        existingCourse.click()

        # See if we are taken to the new course page
        self.wait.until(EC.title_contains(newCourseName))

if __name__ == "__main__":
    unittest.main()

