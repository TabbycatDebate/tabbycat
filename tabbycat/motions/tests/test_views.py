from django.test import TestCase

from utils.tests import ConditionalTournamentViewLoadTest


class PublicMotionStatisticsViewTest(ConditionalTournamentViewLoadTest, TestCase):
    view_name = 'motions-public-statistics'
    view_toggle = 'tab_release__motion_tab_released'
