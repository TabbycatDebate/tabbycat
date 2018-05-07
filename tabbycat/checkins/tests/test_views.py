from django.test import TestCase

from utils.tests import AdminTournamentViewDoesLoadTest, AssistantTournamentViewDoesLoadTest, ConditionalTournamentViewLoadTest


class AdminCheckInScanView(AdminTournamentViewDoesLoadTest, TestCase):
    view_name = 'admin-checkin-scan' # DONE


class AssistantCheckInScanView(AssistantTournamentViewDoesLoadTest, TestCase):
    view_name = 'assistant-checkin-scan'


class AdminCheckInStatusView(AdminTournamentViewDoesLoadTest, TestCase):
    view_name = 'admin-checkin-status' # DONE


class AssistantCheckInStatusView(AssistantTournamentViewDoesLoadTest, TestCase):
    view_name = 'assistant-checkin-status'


class PublicCheckInStatusViewTest(ConditionalTournamentViewLoadTest, TestCase):
    view_name = 'public-checkin-status'
    view_toggle = 'public_features__public_checkins'
