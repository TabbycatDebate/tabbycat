from django.test import TestCase
from tournaments.models import Tournament
from participants.models import Adjudicator, Institution, Speaker, Team
from venues.models import Venue


class BaseDebateTestCase(TestCase):
    """Currently used in availability and participants tests as a pseudo fixture
    to create teh basic data to simulate simple tournament functions"""

    def setUp(self):
        super(BaseDebateTestCase, self).setUp()
        # add test models
        self.t = Tournament(slug="tournament")
        self.t.save()
        for i in range(4):
            ins = Institution(code="INS%s" % i, name="Institution %s" % i)
            ins.save()
            for j in range(3):
                team = Team(tournament=self.t, institution=ins, reference="Team%s%s" % (i, j))
                team.save()
                for k in range(2):
                    speaker = Speaker(team=team, name="Speaker%s%s%s" % (i, j, k))
                    speaker.save()
            for j in range(2):
                adj = Adjudicator(tournament=self.t, institution=ins,
                                  name="Adjudicator%s%s" % (i, j), test_score=0)
                adj.save()

        for i in range(8):
            venue = Venue(name="Venue %s" % i)
            venue.priority = i
            venue.save()

            venue = Venue(name="IVenue %s" % i)
            venue.priority = i
            venue.save()
