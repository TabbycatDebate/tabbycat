from django.test import TestCase

from ..base import StandingsError
from ..teams import TeamStandingsGenerator

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Institution, Team
from results.models import BallotSubmission, TeamScore
from tournaments.models import Round, Tournament
from venues.models import Venue


# TODO does it ignore unconfirmed ballot submissions?
# TODO can it handle uneven numbers of adjudicators?

# TODO Have classes to check each metric annotator in isolation
# TODO Have classes to check each ranking annotator in isolation


class TestTrivialStandings(TestCase):
    """Tests cases with just two teams and one round.

    Mostly intended to check that it doesn't crash under lots of different
    configurations, rather than check the results of the ordering or aggregation
    functions themselves."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="trivialstandingstest", name="Trivial standings test")
        self.team1 = Team.objects.create(tournament=self.tournament, reference="1", use_institution_prefix=False)
        self.team2 = Team.objects.create(tournament=self.tournament, reference="2", use_institution_prefix=False)
        adj = Adjudicator.objects.create(tournament=self.tournament, name="Adjudicator")
        rd = Round.objects.create(tournament=self.tournament, seq=1)
        debate = Debate.objects.create(round=rd)
        self.dt0 = DebateTeam.objects.create(debate=debate, team=self.team1, side=DebateTeam.SIDE_AFF)
        self.dt1 = DebateTeam.objects.create(debate=debate, team=self.team2, side=DebateTeam.SIDE_NEG)
        DebateAdjudicator.objects.create(debate=debate, adjudicator=adj, type=DebateAdjudicator.TYPE_CHAIR)
        ballotsub = BallotSubmission.objects.create(debate=debate, confirmed=True)
        TeamScore.objects.create(debate_team=self.dt0, ballot_submission=ballotsub,
            margin=+1, points=1, score=263, win=True,  votes_given=1, votes_possible=1)
        TeamScore.objects.create(debate_team=self.dt1, ballot_submission=ballotsub,
            margin=-1, points=0, score=261, win=False, votes_given=0, votes_possible=1)

    def tearDown(self):
        self.dt0.delete()
        self.dt1.delete()
        self.tournament.delete()

    def test_no_rankings(self):
        generator = TeamStandingsGenerator(('points',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['points'], 1)
        self.assertEqual(standings.get_standing(self.team2).metrics['points'], 0)

    def test_points(self):
        generator = TeamStandingsGenerator(('points',), ('rank',))
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['points'], 1)
        self.assertEqual(standings.get_standing(self.team2).metrics['points'], 0)
        self.assertEqual(standings.get_standing(self.team1).rankings['rank'], (1, False))
        self.assertEqual(standings.get_standing(self.team2).rankings['rank'], (2, False))

    def test_speaks(self):
        generator = TeamStandingsGenerator(('speaks_sum',), ('rank',))
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['speaks_sum'], 263)
        self.assertEqual(standings.get_standing(self.team2).metrics['speaks_sum'], 261)
        self.assertEqual(standings.get_standing(self.team1).rankings['rank'], (1, False))
        self.assertEqual(standings.get_standing(self.team2).rankings['rank'], (2, False))

    def test_points_speaks_subrank(self):
        generator = TeamStandingsGenerator(('points', 'speaks_sum'), ('rank', 'subrank'))
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['points'], 1)
        self.assertEqual(standings.get_standing(self.team2).metrics['points'], 0)
        self.assertEqual(standings.get_standing(self.team1).metrics['speaks_sum'], 263)
        self.assertEqual(standings.get_standing(self.team2).metrics['speaks_sum'], 261)
        self.assertEqual(standings.get_standing(self.team1).rankings['subrank'], (1, False))
        self.assertEqual(standings.get_standing(self.team2).rankings['subrank'], (1, False))

    def test_wbw_first_error(self):
        self.assertRaises(ValueError, TeamStandingsGenerator, ('wbw', 'points'), ('rank',))

    def test_double_metric_error(self):
        self.assertRaises(StandingsError, TeamStandingsGenerator, ('points', 'wbw', 'points'), ('rank',))


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
        sides = [DebateTeam.SIDE_AFF, DebateTeam.SIDE_NEG]

        for r, debatedict in enumerate(testdata["teamscores"]):
            rd = Round.objects.create(tournament=tournament, seq=r, abbreviation="R{:d}".format(r))
            for adj, venue, (teamnames, teamscores) in zip(adjs, venues, debatedict.items()):
                debate = Debate.objects.create(round=rd, venue=venue)
                for team, side in zip(teamnames, sides):
                    DebateTeam.objects.create(debate=debate, team=teams[team], side=side)
                DebateAdjudicator.objects.create(debate=debate, adjudicator=adj, type=DebateAdjudicator.TYPE_CHAIR)
                ballotsub = BallotSubmission.objects.create(debate=debate, confirmed=True)
                for team, teamscore_dict in teamscores.items():
                    dt = DebateTeam.objects.get(debate=debate, team=teams[team])
                    TeamScore.objects.create(debate_team=dt, ballot_submission=ballotsub, **teamscore_dict)

        return tournament, teams

    def teardown_testdata(self, tournament):
        tournament.delete()

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
