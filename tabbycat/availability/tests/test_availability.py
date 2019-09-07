from participants.models import Adjudicator, Institution
from tournaments.models import Round
from utils.tests import BaseMinimalTournamentTestCase

from ..utils import activate_all, set_availability


class TestAvailability(BaseMinimalTournamentTestCase):

    def setUp(self):
        super().setUp()
        self.round = Round.objects.create(tournament=self.tournament, seq=1)

    def tearDown(self):
        super().tearDown()
        self.round.delete()

    def test_all_active(self):
        set_availability(Adjudicator.objects.all(), self.round)
        self.assertEqual(8, Adjudicator.objects.count())
        self.assertEqual(8, self.round.active_adjudicators.count())

    def test_one_disabled(self):
        set_availability(Adjudicator.objects.exclude(name="Adjudicator00"), self.round)
        self.assertEqual(8, Adjudicator.objects.count())
        self.assertEqual(7, self.round.active_adjudicators.count())

    def test_activate_all(self):
        Adjudicator.objects.create(institution=Institution.objects.get(code="INS0"), name="Unattached")
        activate_all(self.round)
        self.assertEqual(8, self.round.active_adjudicators.count())
        self.assertEqual(12, self.round.active_teams.count())
        self.assertEqual(8, self.round.active_venues.count())
