"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.conf import settings
settings.configure()
from django.test import TestCase
from debate.models import Institution, Team, Speaker, Adjudicator, Debate, Round, Venue, DebateTeam

class BaseTest(TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        # add test models
        for i in range(4):
            ins = Institution(code="INS%s"%i, name="Institution %s"%i)
            ins.save()
            for j in range(3):
                team = Team(institution=ins, name="Team%s%s" % (i,j))
                team.save()
                for k in range(2):
                    speaker = Speaker(team=team, name="Speaker%s%s%s" % (i,j,k))
                    speaker.save()
            for j in range(2):
                adj = Adjudicator(institution=ins, name="Adjudicator%s%s" %
                                  (i,j), test_score=0)
                adj.save()

        for i in range(8):
            venue = Venue(name="Venue %s" % i)
            venue.priority = i
            venue.save()

            venue = Venue(name="IVenue %s" % i)
            venue.priority = i
            venue.save()

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

class TestInstitution(BaseTest):
    def test_objects(self):
        self.failUnlessEqual(4, Institution.objects.count())

class TestAdjudicator(BaseTest):
    def test_objects(self):
        self.failUnlessEqual(8, Adjudicator.objects.count())

class TestAdjudicatorDisable(BaseTest):
    def setUp(self):
        super(TestAdjudicatorDisable, self).setUp()
        self.round = Round(seq=1)
        self.round.save()
        self.activate_all_adj(self.round)

        adj = Adjudicator.objects.get(name="Adjudicator00")
        self.round.activate_adjudicator(adj, False)

    def test_objects(self):
        self.failUnlessEqual(8, Adjudicator.objects.count())

    def test_active(self):
        self.failUnlessEqual(7, self.round.active_adjudicators.count())

class RandomDrawTests(BaseTest):

    def setUp(self):
        super(RandomDrawTests, self).setUp()
        self.round = Round(seq=2, type=Round.DRAW_RANDOM)
        self.round.save()
        self.activate_all_adj(self.round)
        self.activate_all_teams(self.round)
        self.activate_venues(self.round)

    def test_std(self):
        self.round.draw()

        self.failUnlessEqual(6, Debate.objects.count())
        self.failUnlessEqual(12, DebateTeam.objects.count())

        for team in Team.objects.all():
            self.failUnlessEqual(1, DebateTeam.objects.filter(team=team).count())

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

