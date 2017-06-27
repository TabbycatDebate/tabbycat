from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.tests import BaseSeleniumTestCase
from django.test import TestCase


class CoreFunctionsTests(BaseSeleniumTestCase):

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('admin')
        password_input = self.selenium.find_element_by_name("continue").click()
        try:
            wait = WebDriverWait(self.selenium, 5) # Assert login was success
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#messages-container > div.alert-success")))
        finally:
            self.selenium.quit()