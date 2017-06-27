from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from utils.tests import BaseSeleniumTestCase
from django.test import TestCase

# team_tab_released
# speaker_tab_released
# replies_tab_released
# motion_tab_released


class CoreStandingsTests(BaseSeleniumTestCase):

    unset_preferences = None
    round_seq = None
    set_preferences = ['tab_release__speaker_tab_released',
                       'tab_release__team_tab_released',
                       'tab_release__replies_tab_released',
                       'tab_release__motion_tab_released']

    def setUp(self):
        from tournaments.models import Tournament
        self.t = Tournament.objects.first()
        self.t.preferences['tab_release__speaker_tab_released'] = True
        self.t.save()
        print('tournament', self.t)

    def get_view_url(self, view_name=None):
        if not view_name:
            view_name = self.view_name
        from django.core.urlresolvers import reverse
        return reverse(view_name, kwargs=self.get_url_kwargs())

    def get_url_kwargs(self):
        kwargs = {'tournament_slug': self.t.slug}
        if self.round_seq is not None:
            kwargs['round_seq'] = self.round_seq
        return kwargs

    def test_speaker_standings(self):
        test_url = self.get_view_url('standings-public-tab-speaker')
        self.selenium.get('%s%s' % (self.live_server_url, test_url))
        print('%s%s' % (self.live_server_url, test_url))

        try:
            wait = WebDriverWait(self.selenium, 25) # Assert login was success
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#messages-container > div.alert-success")))
        finally:
            self.selenium.quit()

    #     username_input = self.selenium.find_element_by_name("username")
    #     username_input.send_keys('admin')
    #     password_input = self.selenium.find_element_by_name("password")
    #     password_input.send_keys('admin')
    #     password_input = self.selenium.find_element_by_name("continue").click()
    #     try:
    #         wait = WebDriverWait(self.selenium, 5) # Assert login was success
    #         wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#messages-container > div.alert-success")))
    #     finally:
    #         self.selenium.quit()
