import logging

from django.test import TestCase

from utils.tests import AdminTournamentViewSimpleLoadTestMixin, suppress_logs


class EditDebateVenuesViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-debate-venues'
    round_seq = 4

    def test_authenticated_response(self):
        with suppress_logs('breakqual.utils', logging.INFO):
            super().test_authenticated_response()
