from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import unittest

# Create a new instance of the Firefox driver
from selenium.webdriver.support.wait import WebDriverWait

class AddCourseTest(unittest.TestCase):

  def setUp(self):
    self.driver = webdriver.Firefox()

  def tearDown(self):
    self.driver.close()

  def testSchoolName(self):
    self.driver.get("http://localhost:8000")

    addCourseButton = self.driver.find_element_by_id("add-course-btn")
    addCourseButton.click()

    schoolInput = self.driver.find_element_by_id("str_school")

    schoolInput.send_keys("harvard u")

    wait = WebDriverWait(self.driver, 10)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ui-menu-item")))

    schoolInput.send_keys(Keys.DOWN)

    autocompleteMenuItem = self.driver.find_element_by_id("ui-active-menuitem")
    autocompleteMenuItem.click()

    self.assertEqual(schoolInput.get_attribute("value"), "Harvard University")

    schoolId = self.driver.find_element_by_id("id_school")

    self.assertEqual(schoolId.get_attribute("value"), "1817")
