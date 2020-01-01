from django.test import TestCase

from utils.tests import AdminTournamentViewSimpleLoadTestMixin


class EditDebateVenuesViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-debate-venues'
    round_seq = 4
