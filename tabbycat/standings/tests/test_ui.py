from selenium.webdriver.support.ui import WebDriverWait

from utils.tests import SeleniumTournamentTestCase


class CoreStandingsTests(SeleniumTournamentTestCase):

    set_preferences = ['tab_release__speaker_tab_released',
                       'tab_release__team_tab_released',
                       'tab_release__replies_tab_released',
                       'tab_release__motion_tab_released']

    def test_speaker_standings(self):
        test_url = self.reverse_url('standings-public-tab-speaker')
        self.selenium.get('%s%s' % (self.live_server_url, test_url))
        WebDriverWait(self.selenium, 5).until(
            lambda driver: driver.find_element_by_css_selector('.table'))

        tbody = self.selenium.find_elements_by_css_selector(".table tbody")[0]
        rows = tbody.find_elements_by_tag_name("tr")

        def assert_row_state(row, rank, name):
            rank_cell_text = row.find_elements_by_tag_name("td")[0].text
            name_cell_text = row.find_elements_by_tag_name("td")[1].text
            self.assertTrue(rank in rank_cell_text)
            self.assertTrue(name in name_cell_text)

        assert_row_state(rows[0], str(1), "Earnest Becker")
        assert_row_state(rows[1], str(2), "Timmy Craig")
        assert_row_state(rows[2], str(3), "Kyle Ruiz")
        assert_row_state(rows[-2], str(71), "Claire Dunn")
        assert_row_state(rows[-1], str(72), "Willis Carson")
        # TODO: test people of equal ranks
        assert_row_state(rows[50], str(51), "Phil Lyons")

    def test_reply_standings(self):
        test_url = self.reverse_url('standings-public-tab-replies')
        self.selenium.get('%s%s' % (self.live_server_url, test_url))
        WebDriverWait(self.selenium, 5).until(
            lambda driver: driver.find_element_by_css_selector('.table'))

        tbody = self.selenium.find_elements_by_css_selector(".table tbody")[0]
        rows = tbody.find_elements_by_tag_name("tr")

        def assert_row_state(row, rank, name):
            rank_cell_text = row.find_elements_by_tag_name("td")[0].text
            name_cell_text = row.find_elements_by_tag_name("td")[1].text
            self.assertTrue(rank in rank_cell_text)
            self.assertTrue(name in name_cell_text)

        assert_row_state(rows[0], str(1), "Felicia Welch")
        assert_row_state(rows[1], str(2), "Casey Sparks")
        assert_row_state(rows[2], str(3), "Marty Love")
        assert_row_state(rows[-2], str(23), "Emilio Simmons")
        assert_row_state(rows[-1], str(24), "Gail Adkins")
