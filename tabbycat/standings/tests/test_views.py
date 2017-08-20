from django.test import TestCase

from utils.tests import ConditionalTournamentViewBasicCheck


class PublicDiversityViewTest(ConditionalTournamentViewBasicCheck, TestCase):
    view_name = 'standings-public-diversity'
    view_toggle = 'public_features__public_diversity'


class PublicTeamStandingsViewTest(ConditionalTournamentViewBasicCheck, TestCase):
    view_name = 'standings-public-teams-current'
    view_toggle = 'public_features__public_team_standings'


class PublicRepliesTabViewTest(ConditionalTournamentViewBasicCheck, TestCase):
    view_name = 'standings-public-tab-replies'
    view_toggle = 'tab_release__replies_tab_released'


class PublicMotionsTabViewTest(ConditionalTournamentViewBasicCheck, TestCase):
    view_name = 'standings-public-tab-motions'
    view_toggle = 'tab_release__motion_tab_released'
