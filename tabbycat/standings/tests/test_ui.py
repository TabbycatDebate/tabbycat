from selenium.webdriver.support.ui import WebDriverWait

from utils.tests import BaseSeleniumTournamentTestCase


class CoreStandingsTests(BaseSeleniumTournamentTestCase):

    set_preferences = ['tab_release__speaker_tab_released',
                       'tab_release__team_tab_released',
                       'tab_release__replies_tab_released',
                       'tab_release__motion_tab_released']

    def test_speaker_standings(self):
        test_url = self.get_view_url('standings-public-tab-speaker')
        self.selenium.get('%s%s' % (self.live_server_url, test_url))

        timeout = 5
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_css_selector('#messages-container > div.alert-success'))
