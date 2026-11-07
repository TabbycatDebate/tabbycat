from django.test import TestCase

from utils.tests import AdminTournamentViewSimpleLoadTestMixin


class EditDebateAdjudicatorsViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-debate-adjudicators'
    round_seq = 1

    def test_authenticated_response(self):
        super().test_authenticated_response()


class EditPanelAdjudicatorsViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-panel-adjudicators'
    round_seq = 1

    def test_authenticated_response(self):
        super().test_authenticated_response()
