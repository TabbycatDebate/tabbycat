from django.test import TestCase

from tournaments.models import Tournament, Round
from participants.models import Institution, Team, Speaker, Adjudicator
from venues.models import Venue
from draw.models import Debate, DebateTeam
from adjallocation.models import DebateAdjudicator
from results.models import BallotSubmission, TeamScore


# does it ignore unconfirmed ballot submissions?
# can it handle uneven numbers of adjudicators?

class TestBasicStandings(TestCase):

    TEAMS = "ABCD"

    testdata = dict()
    testdata[1] = {
        'standings': {'A': {'against': {'B': 1, 'C': 1, 'D': 'n/a'},
                            'draw_strength': 4,
                            'margin': -7.0,
                            'points': 2,
                            'score': 806.5},
                      'B': {'against': {'A': 1, 'C': 'n/a', 'D': 0},
                            'draw_strength': 5,
                            'margin': -11.0,
                            'points': 1,
                            'score': 785.0},
                      'C': {'against': {'A': 0, 'B': 'n/a', 'D': 2},
                            'draw_strength': 4,
                            'margin': 24.0,
                            'points': 2,
                            'score': 797.5},
                      'D': {'against': {'A': 'n/a', 'B': 1, 'C': 0},
                            'draw_strength': 5,
                            'margin': -6.0,
                            'points': 1,
                            'score': 763.0}},
        'teams': 'ABCD',
        'teamscores':
            [{'AB': {'A': {'margin': 8.0, 'points': 1, 'score': 269.5, 'win': True},
                     'B': {'margin': -8.0, 'points': 0, 'score': 261.5, 'win': False}},
              'CD': {'C': {'margin': 13.5, 'points': 1, 'score': 262.5, 'win': True},
                     'D': {'margin': -13.5, 'points': 0, 'score': 249.0, 'win': False}}},
             {'AC': {'A': {'margin': 3.0, 'points': 1, 'score': 277.0, 'win': True},
                     'C': {'margin': -3.0, 'points': 0, 'score': 274.0, 'win': False}},
              'BD': {'B': {'margin': -21.0, 'points': 0, 'score': 245.5, 'win': False},
                     'D': {'margin': 21.0, 'points': 1, 'score': 266.5, 'win': True}}},
             {'AB': {'A': {'margin': -18.0, 'points': 0, 'score': 260.0, 'win': False},
                     'B': {'margin': 18.0, 'points': 1, 'score': 278.0, 'win': True}},
              'CD': {'C': {'margin': 13.5, 'points': 1, 'score': 261.0, 'win': True},
                     'D': {'margin': -13.5, 'points': 0, 'score': 247.5, 'win': False}}}]
    }

    def setup_testdata(self, testdata):
        self.t = Tournament.objects.create(slug="basicstandingstest", name="Basic standings test")
        self.teams = dict()
        for team_name in testdata["teams"]:
            inst = Institution.objects.create(code=team_name, name=team_name)
            team = Team.objects.create(tournament=self.t, institution=inst, reference=team_name, use_institution_prefix=False)
            self.teams[team_name] = team
        inst = Institution.objects.create(code="Adjs", name="Adjudicators")
        for i in range(len(testdata["teams"])//2):
            Adjudicator.objects.create(tournament=self.t, institution=inst, name="Adjudicator {:d}".format(i), test_score=5)
            Venue.objects.create(name="Venue {:d}".format(i), priority=10)
        adjs = list(Adjudicator.objects.all())
        venues = list(Venue.objects.all())
        positions = [DebateTeam.POSITION_AFFIRMATIVE, DebateTeam.POSITION_NEGATIVE]

        for r, debatedict in enumerate(testdata["teamscores"]):
            rd = Round.objects.create(tournament=self.t, seq=r, abbreviation="R{:d}".format(r))
            for adj, venue, (teams, teamscores) in zip(adjs, venues, debatedict.items()):
                debate = Debate.objects.create(round=rd, venue=venue)
                for team, pos in zip(teams, positions):
                    DebateTeam.objects.create(debate=debate, team=self.teams[team], position=pos)
                DebateAdjudicator.objects.create(debate=debate, adjudicator=adj, type=DebateAdjudicator.TYPE_CHAIR)
                ballotsub = BallotSubmission.objects.create(debate=debate, confirmed=True)
                for team, teamscore_dict in teamscores.items():
                    dt = DebateTeam.objects.get(debate=debate, team=self.teams[team])
                    TeamScore.objects.create(debate_team=dt, ballot_submission=ballotsub, **teamscore_dict)

    def tearDown(self):
        self.t.delete()
        del self.t
        del self.teams

    def test_setup(self):
        self.setup_testdata(self.testdata[1])