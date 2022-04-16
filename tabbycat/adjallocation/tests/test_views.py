import logging

from django.test import TestCase

from utils.tests import AdminTournamentViewSimpleLoadTestMixin, suppress_logs


class EditDebateAdjudicatorsViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-debate-adjudicators'
    round_seq = 1

    def test_authenticated_response(self):
        with suppress_logs('breakqual.utils', logging.INFO):
            super().test_authenticated_response()


class EditPanelAdjudicatorsViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-panel-adjudicators'
    round_seq = 1

    def test_authenticated_response(self):
        with suppress_logs('breakqual.utils', logging.INFO):
            super().test_authenticated_response()
