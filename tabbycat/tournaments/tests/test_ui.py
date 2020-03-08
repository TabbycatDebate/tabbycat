from django.contrib.auth.models import User
from selenium.webdriver.support.ui import WebDriverWait

from utils.tests import SeleniumTournamentTestCase


class CoreFunctionsTests(SeleniumTournamentTestCase):

    def test_login(self):
        user = User.objects.create_user('testadmin', '', 'testadmin')
        user.is_superuser = True
        user.save()

        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('testadmin')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('testadmin')
        password_input = self.selenium.find_element_by_name("continue").click()

        # Wait until the response is received
        timeout = 5
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_css_selector('#messages-container > .alert'))
