from django.test import TestCase

from utils.tests import ConditionalTournamentViewBasicCheckMixin


class PublicDiversityViewTest(ConditionalTournamentViewBasicCheckMixin, TestCase):
    view_name = 'standings-public-diversity'
    view_toggle = 'public_features__public_diversity'


class PublicTeamStandingsViewTest(ConditionalTournamentViewBasicCheckMixin, TestCase):
    view_name = 'standings-public-teams-current'
    view_toggle = 'public_features__public_team_standings'


class PublicRepliesTabViewTest(ConditionalTournamentViewBasicCheckMixin, TestCase):
    view_name = 'standings-public-tab-replies'
    view_toggle = 'tab_release__replies_tab_released'


class PublicMotionsTabViewTest(ConditionalTournamentViewBasicCheckMixin, TestCase):
    view_name = 'standings-public-tab-motions'
    view_toggle = 'tab_release__motion_tab_released'
