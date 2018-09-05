from django.test import TestCase

from utils.tests import AdminTournamentViewSimpleLoadTestMixin, AssistantTournamentViewSimpleLoadTestMixin, ConditionalTournamentViewSimpleLoadTestMixin


class AdminCheckInScanView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-checkin-scan' # DONE


class AssistantCheckInScanView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-checkin-scan'


class AdminCheckInStatusView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-checkin-status' # DONE


class AssistantCheckInStatusView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-checkin-status'


class PublicCheckInStatusViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'checkins-public-status'
    view_toggle_preference = 'public_features__public_checkins'
