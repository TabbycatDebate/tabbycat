import logging

from django.test import TestCase

from utils.tests import ConditionalTournamentViewSimpleLoadTestMixin, suppress_logs


class PublicStandingsTestMixin(ConditionalTournamentViewSimpleLoadTestMixin):
    """Suppresses standings logging output."""

    def test_view_enabled(self):
        with suppress_logs('standings.metrics', logging.INFO):
            super().test_view_enabled()


class PublicTeamStandingsViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'standings-public-teams-current'
    view_toggle_preference = 'public_features__public_team_standings'


class PublicTeamTabViewTest(PublicStandingsTestMixin, TestCase):
    view_name = 'standings-public-tab-team'
    view_toggle_preference = 'tab_release__team_tab_released'


class PublicSpeakerTabViewTest(PublicStandingsTestMixin, TestCase):
    view_name = 'standings-public-tab-speaker'
    view_toggle_preference = 'tab_release__speaker_tab_released'


class PublicRepliesTabViewTest(PublicStandingsTestMixin, TestCase):
    view_name = 'standings-public-tab-replies'
    view_toggle_preference = 'tab_release__replies_tab_released'


class PublicAdjudicatorTabViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'standings-public-adjudicators-tab'
    view_toggle_preference = 'tab_release__adjudicators_tab_released'


class PublicDiversityViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'standings-public-diversity'
    view_toggle_preference = 'public_features__public_diversity'
