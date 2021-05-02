from django.test import TestCase

from utils.tests import AdminTournamentViewSimpleLoadTestMixin, AssistantTournamentViewSimpleLoadTestMixin, ConditionalTournamentViewSimpleLoadTestMixin


class AdminCheckInPreScanView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-checkin-prescan'


class AssistantCheckInPreScanView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-checkin-prescan'


class AdminCheckInPeopleStatusView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-people-statuses'


class AssistantCheckInPeopleStatusView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-people-statuses'


class AdminCheckInVenuesStatusView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-venues-statuses'


class AssistantCheckInVenuesStatusView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-venues-statuses'


class AdminCheckInIdentifiersView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-checkin-identifiers'


class AssistantCheckInIdentifiersView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-checkin-identifiers'


class AdminCheckInSpeakersPrintablesView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-checkin-print'
    view_reverse_kwargs = {'kind': 'speakers'}


class AssistantCheckInSpeakersPrintablesView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-checkin-print'
    view_reverse_kwargs = {'kind': 'speakers'}


class AdminCheckInAdjudicatorsPrintablesView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-checkin-print'
    view_reverse_kwargs = {'kind': 'adjudicators'}


class AssistantCheckInAdjudicatorsPrintablesView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-checkin-print'
    view_reverse_kwargs = {'kind': 'adjudicators'}


class AdminCheckInVenuesPrintablesView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'admin-checkin-print'
    view_reverse_kwargs = {'kind': 'venues'}


class AssistantCheckInVenuesPrintablesView(AssistantTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'assistant-checkin-print'
    view_reverse_kwargs = {'kind': 'venues'}


class PublicCheckInStatusViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'checkins-public-status'
    view_toggle_preference = 'public_features__public_checkins'

# These require the ability to test POST views
# class AdminCheckInSpeakersGenerateView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
#     view_name = 'admin-checkin-generate'
#     view_reverse_kwargs = {'kind': 'speakers'}
#
# class AdminCheckInAdjudicatorsGenerateView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
#     view_name = 'admin-checkin-generate'
#     view_reverse_kwargs = {'kind': 'adjudicators'}
#
# class AdminCheckInVenuesGenerateView(AdminTournamentViewSimpleLoadTestMixin, TestCase):
#     view_name = 'admin-checkin-generate'
#     view_reverse_kwargs = {'kind': 'venues'}
