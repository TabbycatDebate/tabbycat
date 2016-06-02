from utils.tests import BaseDebateTestCase

from tournaments.models import Round
from draw.manager import DrawManager
from draw.models import Debate, DebateTeam
from participants.models import Team, Adjudicator
from venues.models import Venue


class TestAvailabilities(BaseDebateTestCase):

    def activate_all_adj(self, r):
        for adj in Adjudicator.objects.all():
            r.activate_adjudicator(adj, True)

    def activate_all_venue(self, r):
        for venue in Venue.objects.all():
            r.activate_venue(venue, True)

    def activate_all_teams(self, r):
        for team in Team.objects.all():
            r.activate_team(team, True)

    def activate_venues(self, r):
        for venue in Venue.objects.all():
            if venue.name.startswith("Venue"):
                r.activate_venue(venue, True)


class TestAdjudicatorDisable(TestAvailabilities):
    def setUp(self):
        super(TestAdjudicatorDisable, self).setUp()
        self.round = Round(tournament=self.t, seq=1)
        self.round.save()
        self.activate_all_adj(self.round)

        adj = Adjudicator.objects.get(name="Adjudicator00")
        self.round.activate_adjudicator(adj, False)

    def test_objects(self):
        self.failUnlessEqual(8, Adjudicator.objects.count())

    def test_active(self):
        self.failUnlessEqual(7, self.round.active_adjudicators.count())


class RandomDrawTests(TestAvailabilities):

    def setUp(self):
        super(RandomDrawTests, self).setUp()
        self.round = Round(tournament=self.t, seq=2, draw_type=Round.DRAW_RANDOM)
        self.round.save()
        self.activate_all_adj(self.round)
        self.activate_all_teams(self.round)
        self.activate_venues(self.round)

    def test_std(self):
        DrawManager(self.round).create()

        self.failUnlessEqual(6, Debate.objects.count())
        self.failUnlessEqual(12, DebateTeam.objects.count())

        for team in Team.objects.all():
            self.failUnlessEqual(1, DebateTeam.objects.filter(team=team).count())
