import logging

from django.test import TestCase

from utils.tests import ConditionalTournamentViewLoadTest, suppress_logs


class PublicTeamStandingsViewTest(ConditionalTournamentViewLoadTest, TestCase):
    view_name = 'standings-public-teams-current'
    view_toggle = 'public_features__public_team_standings'


class PublicTeamTabViewTest(ConditionalTournamentViewLoadTest, TestCase):
    view_name = 'standings-public-tab-team'
    view_toggle = 'tab_release__team_tab_released'


class PublicSpeakerTabViewTest(ConditionalTournamentViewLoadTest, TestCase):
    view_name = 'standings-public-tab-speaker'
    view_toggle = 'tab_release__speaker_tab_released'


class PublicRepliesTabViewTest(ConditionalTournamentViewLoadTest, TestCase):
    view_name = 'standings-public-tab-replies'
    view_toggle = 'tab_release__replies_tab_released'

    def test_set_preference(self):
        with suppress_logs('standings.metrics', logging.INFO):
            super().test_set_preference()

    def test_unset_preference(self):
        with suppress_logs('standings.metrics', logging.INFO):
            super().test_unset_preference()


class PublicAdjudicatorTabViewTest(ConditionalTournamentViewLoadTest, TestCase):
    view_name = 'standings-public-adjudicators-tab'
    view_toggle = 'tab_release__adjudicators_tab_released'


class PublicDiversityViewTest(ConditionalTournamentViewLoadTest, TestCase):
    view_name = 'standings-public-diversity'
    view_toggle = 'public_features__public_diversity'
