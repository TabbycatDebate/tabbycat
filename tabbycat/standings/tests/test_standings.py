from django.test import TestCase

from ..teams import TeamStandingsGenerator

from tournaments.models import Round, Tournament
from participants.models import Adjudicator, Institution, Team
from venues.models import Venue
from draw.models import Debate, DebateTeam
from adjallocation.models import DebateAdjudicator
from results.models import BallotSubmission, TeamScore


# TODO does it ignore unconfirmed ballot submissions?
# TODO can it handle uneven numbers of adjudicators?

# TODO Have classes to check each metric annotator in isolation
# TODO Have classes to check each ranking annotator in isolation

class TestBasicStandings(TestCase):

    TEAMS = "ABCD"

    testdata = dict()
    testdata[1] = \
        {'rankings': {('points', 'speaks_sum'): ['A', 'D', 'C', 'B'],
                      ('points', 'speaks_sum', 'draw_strength', 'margin_sum'): ['A', 'D', 'C', 'B']},
         'standings': {'A': {'against': {'B': 2, 'C': 0, 'D': 'n/a'},
                             'draw_strength': 2,
                             'margin_sum': 46.0,
                             'points': 2,
                             'speaks_sum': 804.5},
                       'B': {'against': {'A': 0, 'C': 'n/a', 'D': 0},
                             'draw_strength': 6,
                             'margin_sum': -62.0,
                             'points': 0,
                             'speaks_sum': 753.5},
                       'C': {'against': {'A': 1, 'B': 'n/a', 'D': 1},
                             'draw_strength': 6,
                             'margin_sum': 8.0,
                             'points': 2,
                             'speaks_sum': 784.5},
                       'D': {'against': {'A': 'n/a', 'B': 1, 'C': 1},
                             'draw_strength': 4,
                             'margin_sum': 8.0,
                             'points': 2,
                             'speaks_sum': 787.5}},
         'teams': ['A', 'B', 'C', 'D'],
         'teamscores': [{'AB': {'A': {'margin': 22.5,  'points': 1, 'score': 265.0, 'win': True,  'votes_given': 1, 'votes_possible': 1},
                                'B': {'margin': -22.5, 'points': 0, 'score': 242.5, 'win': False, 'votes_given': 0, 'votes_possible': 1}},
                         'CD': {'C': {'margin': 20.0,  'points': 1, 'score': 273.0, 'win': True,  'votes_given': 1, 'votes_possible': 1},
                                'D': {'margin': -20.0, 'points': 0, 'score': 253.0, 'win': False, 'votes_given': 0, 'votes_possible': 1}}},
                        {'AC': {'A': {'margin': -1.5,  'points': 0, 'score': 263.5, 'win': False, 'votes_given': 0, 'votes_possible': 1},
                                'C': {'margin': 1.5,   'points': 1, 'score': 265.0, 'win': True,  'votes_given': 1, 'votes_possible': 1}},
                         'BD': {'B': {'margin': -14.5, 'points': 0, 'score': 260.0, 'win': False, 'votes_given': 0, 'votes_possible': 1},
                                'D': {'margin': 14.5,  'points': 1, 'score': 274.5, 'win': True,  'votes_given': 1, 'votes_possible': 1}}},
                        {'AB': {'A': {'margin': 25.0,  'points': 1, 'score': 276.0, 'win': True,  'votes_given': 1, 'votes_possible': 1},
                                'B': {'margin': -25.0, 'points': 0, 'score': 251.0, 'win': False, 'votes_given': 0, 'votes_possible': 1}},
                         'CD': {'C': {'margin': -13.5, 'points': 0, 'score': 246.5, 'win': False, 'votes_given': 0, 'votes_possible': 1},
                                'D': {'margin': 13.5,  'points': 1, 'score': 260.0, 'win': True,  'votes_given': 1, 'votes_possible': 1}}}]}

    rankings = ('rank',)

    def setup_testdata(self, testdata):
        tournament = Tournament.objects.create(slug="basicstandingstest", name="Basic standings test")
        teams = dict()
        for team_name in testdata["teams"]:
            inst = Institution.objects.create(code=team_name, name=team_name)
            team = Team.objects.create(tournament=tournament, institution=inst, reference=team_name, use_institution_prefix=False)
            teams[team_name] = team
        inst = Institution.objects.create(code="Adjs", name="Adjudicators")
        for i in range(len(testdata["teams"])//2):
            Adjudicator.objects.create(tournament=tournament, institution=inst, name="Adjudicator {:d}".format(i), test_score=5)
            Venue.objects.create(name="Venue {:d}".format(i), priority=10)
        adjs = list(Adjudicator.objects.all())
        venues = list(Venue.objects.all())
        positions = [DebateTeam.POSITION_AFFIRMATIVE, DebateTeam.POSITION_NEGATIVE]

        for r, debatedict in enumerate(testdata["teamscores"]):
            rd = Round.objects.create(tournament=tournament, seq=r, abbreviation="R{:d}".format(r))
            for adj, venue, (teamnames, teamscores) in zip(adjs, venues, debatedict.items()):
                debate = Debate.objects.create(round=rd, venue=venue)
                for team, pos in zip(teamnames, positions):
                    DebateTeam.objects.create(debate=debate, team=teams[team], position=pos)
                DebateAdjudicator.objects.create(debate=debate, adjudicator=adj, type=DebateAdjudicator.TYPE_CHAIR)
                ballotsub = BallotSubmission.objects.create(debate=debate, confirmed=True)
                for team, teamscore_dict in teamscores.items():
                    dt = DebateTeam.objects.get(debate=debate, team=teams[team])
                    TeamScore.objects.create(debate_team=dt, ballot_submission=ballotsub, **teamscore_dict)

        return tournament, teams

    def teardown_testdata(self, tournament):
        tournament.delete()

    def test_invalid_wbw(self):
        self.assertRaises(ValueError, TeamStandingsGenerator, ('wbw', 'points'), ('rank'))

    def test_standings(self):
        for index, testdata in self.testdata.items():
            tournament, teams = self.setup_testdata(testdata)
            for metrics in testdata["rankings"].keys():
                with self.subTest(index=index, metrics=metrics):
                    generator = TeamStandingsGenerator(metrics, self.rankings)
                    standings = generator.generate(tournament.team_set.all())

                    self.assertEqual(len(standings), len(testdata["standings"]))
                    self.assertEqual(standings.metric_keys, list(metrics))

                    for teamname, expected in testdata["standings"].items():
                        team = teams[teamname]
                        standing = standings.get_standing(team)
                        for metric in metrics:
                            self.assertEqual(standing.metrics[metric], expected[metric])

                    ranked_teams = [teams[x] for x in testdata["rankings"][metrics]]
                    self.assertEqual(ranked_teams, standings.get_instance_list())

    # TODO check that WBW is correct when not in first metrics
    # TODO check that it doesn't break when not all metrics present
    # TODO check that it works for different rounds
