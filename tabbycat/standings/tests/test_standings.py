from django.test import TestCase

from ..base import StandingsError
from ..teams import TeamStandingsGenerator

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Institution, Speaker, Team
from results.models import BallotSubmission, SpeakerScore, TeamScore
from tournaments.models import Round, Tournament
from venues.models import Venue


# TODO does it ignore unconfirmed ballot submissions?
# TODO can it handle uneven numbers of adjudicators?

# TODO Have classes to check each metric annotator in isolation
# TODO Have classes to check each ranking annotator in isolation


class TestTrivialStandings(TestCase):
    """Tests cases with just two teams and two rounds.

    Mostly intended to check that it doesn't crash under lots of different
    configurations, rather than check the results of the ordering or aggregation
    functions themselves."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="trivialstandingstest", name="Trivial standings test")
        self.team1 = Team.objects.create(tournament=self.tournament, reference="1", use_institution_prefix=False)
        self.team2 = Team.objects.create(tournament=self.tournament, reference="2", use_institution_prefix=False)
        adj = Adjudicator.objects.create(tournament=self.tournament, name="Adjudicator")
        for i in [1, 2]:
            rd = Round.objects.create(tournament=self.tournament, seq=i)
            debate = Debate.objects.create(round=rd)
            dt1 = DebateTeam.objects.create(debate=debate, team=self.team1, side=DebateTeam.SIDE_AFF)
            dt2 = DebateTeam.objects.create(debate=debate, team=self.team2, side=DebateTeam.SIDE_NEG)
            DebateAdjudicator.objects.create(debate=debate, adjudicator=adj, type=DebateAdjudicator.TYPE_CHAIR)
            ballotsub = BallotSubmission.objects.create(debate=debate, confirmed=True)
            TeamScore.objects.create(debate_team=dt1, ballot_submission=ballotsub,
                margin=+2*i, points=1, score=100+i, win=True,  votes_given=1, votes_possible=1)
            TeamScore.objects.create(debate_team=dt2, ballot_submission=ballotsub,
                margin=-2*i, points=0, score=100-i, win=False, votes_given=0, votes_possible=1)

    def tearDown(self):
        DebateTeam.objects.filter(team__tournament=self.tournament).delete()
        self.tournament.delete()

    def test_points(self):
        generator = TeamStandingsGenerator(('points',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['points'], 2)
        self.assertEqual(standings.get_standing(self.team2).metrics['points'], 0)

    def test_points210(self):
        generator = TeamStandingsGenerator(('points210',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['points210'], 4)
        self.assertEqual(standings.get_standing(self.team2).metrics['points210'], 2)

    def test_wins(self):
        generator = TeamStandingsGenerator(('wins',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['wins'], 2)
        self.assertEqual(standings.get_standing(self.team2).metrics['wins'], 0)

    def test_speaks_sum(self):
        generator = TeamStandingsGenerator(('speaks_sum',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['speaks_sum'], 203)
        self.assertEqual(standings.get_standing(self.team2).metrics['speaks_sum'], 197)

    def test_speaks_avg(self):
        generator = TeamStandingsGenerator(('speaks_avg',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['speaks_avg'], 101.5)
        self.assertEqual(standings.get_standing(self.team2).metrics['speaks_avg'], 98.5)

    def test_speaks_ind_avg(self):
        # The speaks_ind_avg metric relies in speaker scores, not team scores
        speaker1 = Speaker.objects.create(team=self.team1, name="Speaker 1")
        speaker2 = Speaker.objects.create(team=self.team2, name="Speaker 2")
        for i in [1, 2]:
            rd = Round.objects.get(tournament=self.tournament, seq=i)
            dt1 = DebateTeam.objects.get(debate__round=rd, team=self.team1)
            dt2 = DebateTeam.objects.get(debate__round=rd, team=self.team2)
            ballotsub = BallotSubmission.objects.get(debate__round=rd)
            SpeakerScore.objects.create(debate_team=dt1, ballot_submission=ballotsub,
                speaker=speaker1, position=1, score=100+i)
            SpeakerScore.objects.create(debate_team=dt2, ballot_submission=ballotsub,
                speaker=speaker2, position=1, score=100-i)

        generator = TeamStandingsGenerator(('speaks_ind_avg',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['speaks_ind_avg'], 101.5)
        self.assertEqual(standings.get_standing(self.team2).metrics['speaks_ind_avg'], 98.5)

    def test_speaks_stddev(self):
        generator = TeamStandingsGenerator(('speaks_stddev',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertAlmostEqual(standings.get_standing(self.team1).metrics['speaks_stddev'], 0.5)
        self.assertAlmostEqual(standings.get_standing(self.team2).metrics['speaks_stddev'], 0.5)

    def test_draw_strength(self):
        generator = TeamStandingsGenerator(('draw_strength',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['draw_strength'], 0)
        # losing team has faced winning team twice, so draw strength is 2 * 2 = 4
        self.assertEqual(standings.get_standing(self.team2).metrics['draw_strength'], 4)

    def test_draw_strength_speaks(self):
        generator = TeamStandingsGenerator(('draw_strength_speaks',), ())
        standings = generator.generate(self.tournament.team_set.all())
        # teams have faced each other twice, so draw strength is twice opponent's score
        self.assertEqual(standings.get_standing(self.team1).metrics['draw_strength_speaks'], 394)
        self.assertEqual(standings.get_standing(self.team2).metrics['draw_strength_speaks'], 406)

    def test_margin_sum(self):
        generator = TeamStandingsGenerator(('margin_sum',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['margin_sum'], 6)
        self.assertEqual(standings.get_standing(self.team2).metrics['margin_sum'], -6)

    def test_margin_avg(self):
        generator = TeamStandingsGenerator(('margin_avg',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['margin_avg'], 3)
        self.assertEqual(standings.get_standing(self.team2).metrics['margin_avg'], -3)

    def test_num_adjs(self):
        generator = TeamStandingsGenerator(('num_adjs',), ())
        standings = generator.generate(self.tournament.team_set.all())
        # normalized to 3 adjs per debate, so the winning team has 6 adjudicators
        self.assertEqual(standings.get_standing(self.team1).metrics['num_adjs'], 6)
        self.assertEqual(standings.get_standing(self.team2).metrics['num_adjs'], 0)

    def test_wbw(self):
        generator = TeamStandingsGenerator(('points', 'wbw'), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['wbw1'], 'n/a')
        self.assertEqual(standings.get_standing(self.team2).metrics['wbw1'], 'n/a')

    def test_npullups(self):
        generator = TeamStandingsGenerator(('npullups',), ())
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['npullups'], 0)
        self.assertEqual(standings.get_standing(self.team2).metrics['npullups'], 0)

    def test_points_ranked(self):
        generator = TeamStandingsGenerator(('points',), ('rank',))
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['points'], 2)
        self.assertEqual(standings.get_standing(self.team2).metrics['points'], 0)
        self.assertEqual(standings.get_standing(self.team1).rankings['rank'], (1, False))
        self.assertEqual(standings.get_standing(self.team2).rankings['rank'], (2, False))

    def test_speaks_ranked(self):
        generator = TeamStandingsGenerator(('speaks_sum',), ('rank',))
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['speaks_sum'], 203)
        self.assertEqual(standings.get_standing(self.team2).metrics['speaks_sum'], 197)
        self.assertEqual(standings.get_standing(self.team1).rankings['rank'], (1, False))
        self.assertEqual(standings.get_standing(self.team2).rankings['rank'], (2, False))

    def test_points_speaks_subrank(self):
        generator = TeamStandingsGenerator(('points', 'speaks_sum'), ('rank', 'subrank'))
        standings = generator.generate(self.tournament.team_set.all())
        self.assertEqual(standings.get_standing(self.team1).metrics['points'], 2)
        self.assertEqual(standings.get_standing(self.team2).metrics['points'], 0)
        self.assertEqual(standings.get_standing(self.team1).metrics['speaks_sum'], 203)
        self.assertEqual(standings.get_standing(self.team2).metrics['speaks_sum'], 197)
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
