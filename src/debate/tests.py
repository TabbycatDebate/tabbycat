"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from debate.models import Institution, Team, Speaker, Adjudicator, Debate, Round, Venue, DebateTeam

class BaseTest(TestCase):
    def setUp(self):
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
                adj = Adjudicator(institution=ins, name="Adjudicator%s%s" % (i,j))
                adj.save()
        Adjudicator.objects.activate_all()
        
        for i in range(8):
            venue = Venue(name="Venue %s" % i)
            venue.is_active = True
            venue.priority = i
            venue.save()
            
        for i in range(3):
            venue = Venue(name="IVenue %s" % i)
            venue.is_active = False
            venue.priority = i
            venue.save()
                    
                    
class TestInstitution(BaseTest):
    def test_objects(self):
        self.failUnlessEqual(4, Institution.objects.count())
        
class TestAdjudicator(BaseTest):
    def test_objects(self):
        self.failUnlessEqual(8, Adjudicator.objects.count())
    def test_active(self):
        self.failUnlessEqual(8, Adjudicator.active.count())
    def test_inactive(self):
        self.failUnlessEqual(0, Adjudicator.inactive.count())
        
class TestAdjudicatorDisable(BaseTest):
    def setUp(self):
        super(TestAdjudicatorDisable, self).setUp()
        
        adj = Adjudicator.objects.get(name="Adjudicator00")
        adj.is_active = False
        adj.save()
        
    def test_objects(self):
        self.failUnlessEqual(8, Adjudicator.objects.count())
    def test_active(self):
        self.failUnlessEqual(7, Adjudicator.active.count())
    def test_inactive(self):
        self.failUnlessEqual(1, Adjudicator.inactive.count())
       

class TestDrawRandom(BaseTest):
    def test_std(self):
        round = Round()
        round.save()
        round.draw_random()
        
        self.failUnlessEqual(6, Debate.objects.count()) 
        self.failUnlessEqual(12, DebateTeam.objects.count())
        
        for team in Team.objects.all():
            self.failUnlessEqual(1, DebateTeam.objects.filter(team=team).count())
            


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

