from django.test import TestCase

from utils.tests import ConditionalTournamentViewBasicCheckMixin


class PublicMotionStatisticsViewTest(ConditionalTournamentViewBasicCheckMixin, TestCase):
    view_name = 'motions-public-statistics'
    view_toggle = 'tab_release__motion_tab_released'
