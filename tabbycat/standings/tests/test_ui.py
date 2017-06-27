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

        timeout = 10
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_css_selector('.table'))

        rows = self.selenium.find_elements_by_css_selector(".table tbody tr")
        for index, row in enumerate(rows):
            rank_cell = row.find_elements_by_tag_name("td")[0]
            name_cell = row.find_elements_by_tag_name("td")[1]
            print(rank_cell.text, name_cell.text)
