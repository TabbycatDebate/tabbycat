from django.test import TestCase

from utils.tests import AdminTournamentViewSimpleLoadTestMixin


class EditDebateVenuesViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-debate-venues'
    round_seq = 4

    def test_authenticated_response(self):
        super().test_authenticated_response()
