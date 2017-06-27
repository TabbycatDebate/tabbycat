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

        def assertRowState(row, rank, name):
            rankCellText = row.find_elements_by_tag_name("td")[0].text
            self.assertTrue(rank in rankCellText)
            nameCellText = row.find_elements_by_tag_name("td")[1].text
            self.assertTrue(name in nameCellText)

        assertRowState(rows[0], str(1), "Earnest Becker")
        assertRowState(rows[1], str(2), "Timmy Craig")
        assertRowState(rows[1], str(2), "Kyle Ruiz")
        assertRowState(rows[51], str(51), "Phil Lyons")
        assertRowState(rows[-1], str(72), "Willis Carson")