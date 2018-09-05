from django.test import TestCase

from utils.tests import ConditionalTournamentViewSimpleLoadTestMixin


class PublicMotionStatisticsViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'motions-public-statistics'
    view_toggle_preference = 'tab_release__motion_tab_released'
