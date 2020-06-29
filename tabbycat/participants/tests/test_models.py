from participants.models import Adjudicator, Institution
from utils.tests import BaseMinimalTournamentTestCase


class TestInstitution(BaseMinimalTournamentTestCase):
    def test_objects(self):
        self.assertEqual(4, Institution.objects.count())


class TestAdjudicator(BaseMinimalTournamentTestCase):
    def test_objects(self):
        self.assertEqual(8, Adjudicator.objects.count())
