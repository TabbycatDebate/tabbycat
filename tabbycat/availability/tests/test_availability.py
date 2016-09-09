from participants.models import Adjudicator
from tournaments.models import Round
from utils.tests import BaseDebateTestCase

from ..utils import set_availability


class TestAdjudicatorDisable(BaseDebateTestCase):
    def setUp(self):
        super(TestAdjudicatorDisable, self).setUp()
        self.round = Round(tournament=self.t, seq=1)
        self.round.save()
        set_availability(Adjudicator.objects.exclude(name="Adjudicator00"), self.round)

    def test_objects(self):
        self.assertEqual(8, Adjudicator.objects.count())

    def test_active(self):
        self.assertEqual(7, self.round.active_adjudicators.count())
