from availability.utils import activate_all
from draw.manager import DrawManager
from draw.models import DebateTeam
from participants.models import Team
from tournaments.models import Round
from utils.tests import BaseMinimalTournamentTestCase


class RandomDrawTests(BaseMinimalTournamentTestCase):

    def setUp(self):
        super(RandomDrawTests, self).setUp()
        self.round = Round(tournament=self.tournament, seq=2, draw_type=Round.DRAW_RANDOM)
        self.round.save()
        activate_all(self.round)

    def test_std(self):
        DrawManager(self.round).create()

        self.assertEqual(6, self.round.debate_set.count())
        self.assertEqual(12, DebateTeam.objects.filter(debate__round=self.round).count())

        for team in Team.objects.all():
            self.assertEqual(1, DebateTeam.objects.filter(team=team).count())
