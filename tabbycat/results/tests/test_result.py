import logging

from django.test import TestCase

from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Institution, Speaker, Team
from results.models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, TeamScore
from results.result import ConsensusDebateResultWithScores, DebateResultByAdjudicatorWithScores, ResultError    # absolute import to keep logger's name consistent
from tournaments.models import Round, Tournament
from utils.tests import suppress_logs
from venues.models import Venue


# ==============================================================================
# Test decorators
# ==============================================================================

def standard_test(test_fn):
    """Decorator. Tests on all dataset in self.testdata, and all scoresheet
    types listed in the arguments. Tests should take four arguments: self,
    result, testdata and scoresheet_type, where
    `result` is a DebateResult object,
    `testdata` is a value in `BaseTestDebateResult.testdata`, and
    `scoresheet_type` is one of the scoresheet_types.
    """
    def wrapped(self):
      for scoresheet_type in ['high-required']:  # noqa: E111
        # with self.subTest(scoresheet_type=scoresheet_type):
          # noqa: E114 self.set_tournament_preference('scoring', 'scoresheet_type', scoresheet_type)  # noqa: E111
          for key, testdata in self.testdata.items():  # noqa: E111
            with self.subTest(testdata=key):
              if not testdata[scoresheet_type]['valid']:  # noqa: E111
                self.assertRaises(ResultError, self.save_complete_result, testdata)
              else:  # noqa: E111
                self.save_complete_result(testdata)
                result = self.get_result()
                test_fn(self, result, testdata, scoresheet_type)
    return wrapped


def with_preference(section, name, value):
    """Decorator. Sets a tournament preference before it begins the wrapped
    function. The main purpose of this decorator is to be used with other
    decorators, otherwise it could obviously just be achieved with a single
    line at the beginning of the function. This decorator should normally be
    placed first in the decorator chain, so that it is the outermost
    wrapper."""
    def wrap(test_fn):
        def wrapped(self):
            self.set_tournament_preference(section, name, value)
            test_fn(self)
        return wrapped
    return wrap


def incomplete_test(test_fn):
    """Decorator. The test function should somehow make `result` incomplete.
    This then wraps the function to assert that the result does indeed think
    itself to be incomplete."""
    def wrap(self):
        testdata = self.testdata['high']
        if not BallotSubmission.objects.filter(debate=self.debate, confirmed=True).exists():
            self.save_complete_result(testdata)
        result = self.get_result()
        test_fn(self, result)
        self.assertFalse(result.is_complete())
        self.assertFalse(result.is_valid())
    return wrap


def bad_load_assertion_test(test_fn):
    """Decorator. The test function should somehow make `result` incorrectly
    loaded. This then wraps the function to assert that the result does indeed
    think itself to be incorrectly loaded."""
    def wrap(self):
        testdata = self.testdata['high']
        if not BallotSubmission.objects.filter(debate=self.debate, confirmed=True).exists():
            self.save_complete_result(testdata)
        result = self.get_result()
        test_fn(self, result)
        self.assertRaises(AssertionError, result.assert_loaded)
    return wrap


# ==============================================================================
# Base class and mixins
# ==============================================================================

class BaseTestDebateResult(TestCase):

    SIDES = ['aff', 'neg']

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="resulttest", name="ResultTest")
        self.teams = []
        for i in range(2):
            inst = Institution.objects.create(code="Inst{:d}".format(i), name="Institution {:d}".format(i))
            team = Team.objects.create(tournament=self.tournament, institution=inst, reference="Team {:d}".format(i), use_institution_prefix=False)
            self.teams.append(team)
            for j in range(3):
                Speaker.objects.create(team=team, name="Speaker {:d}-{:d}".format(i, j))

        venue = Venue.objects.create(name="Venue", priority=10)

        rd = Round.objects.create(tournament=self.tournament, seq=1, abbreviation="R1")
        self.debate = Debate.objects.create(round=rd, venue=venue)

        sides = [DebateTeam.SIDE_AFF, DebateTeam.SIDE_NEG]
        for team, side in zip(Team.objects.all(), sides):
            DebateTeam.objects.create(debate=self.debate, team=team, side=side)

        inst = Institution.objects.create(code="Adjs", name="Adjudicators")
        self.adjs = [Adjudicator.objects.create(tournament=self.tournament, institution=inst,
                name="Adjudicator {:d}".format(i), base_score=5) for i in range(3)]

    def tearDown(self):
        DebateTeam.objects.all().delete()
        Institution.objects.all().delete()
        self.tournament.delete()

    def set_tournament_preference(self, section, name, value):
        self.tournament.preferences[section + '__' + name] = value
        if name in self.tournament._prefs:    # clear model-level cache
            del self.tournament._prefs[name]

    def get_result(self):
        ballotsub = BallotSubmission.objects.get(debate=self.debate, confirmed=True)
        return self.debate_result_class(ballotsub)

    def save_blank_result(self, nadjs=3, nspeakers=3):

        self.set_tournament_preference('debate_rules', 'substantive_speakers', nspeakers)

        # set debate adjudicators (depends on how many adjs there are, so can't do in setUp())
        self.debate.adjudicators.chair = self.adjs[0]
        self.debate.adjudicators.panellists = self.adjs[1:nadjs]
        with suppress_logs('adjallocation.allocation', logging.INFO):
            self.debate.adjudicators.save()

        # unconfirm existing ballots
        self.debate.ballotsubmission_set.update(confirmed=False)

        ballotsub = BallotSubmission.objects.create(debate=self.debate, confirmed=True,
                submitter_type=BallotSubmission.SUBMITTER_TABROOM)

        return self.debate_result_class(ballotsub)

    def save_complete_result(self, testdata, post_create=None):

        nspeakers = testdata['num_speakers_per_team']

        result = self.save_blank_result(nadjs=testdata['num_adjs'], nspeakers=nspeakers)
        if post_create:
            post_create(result)

        for side, team in zip(self.SIDES, self.teams):
            speakers = team.speaker_set.all()[0:nspeakers]
            for pos, speaker in enumerate(speakers, start=1):
                result.set_speaker(side, pos, speaker)
            result.set_speaker(side, nspeakers+1, speakers[0])
            # ghost fields should be False by default

        self.save_scores_to_result(testdata, result)

        with suppress_logs('results.result', logging.WARNING):
            result.save()

    def _get_speakerscore_in_db(self, side, pos):
        return SpeakerScore.objects.get(
            ballot_submission__debate=self.debate,
            ballot_submission__confirmed=True,
            debate_team__side=side,
            position=pos,
        )

    def _get_teamscore_in_db(self, side):
        return TeamScore.objects.get(
            ballot_submission__debate=self.debate,
            ballot_submission__confirmed=True,
            debate_team__side=side,
        )

    def _unset_sides(self):
        self.debate.sides_confirmed = False
        self.debate.save()


class GeneralSpeakerTestsMixin:

    @standard_test
    def test_save(self, result, testdata, scoresheet_type):
        # Run self.save_complete_result and check completeness
        self.assertTrue(result.is_complete())

    def test_unknown_speaker(self):
        self.save_complete_result(self.testdata['high'])
        result = self.get_result()
        neg_speaker = self.teams[1].speaker_set.first()
        with self.assertLogs('results.result', level=logging.ERROR):
            result.set_speaker('aff', 1, neg_speaker)

    def test_save_speaker_with_unknown_sides(self):
        self._unset_sides()
        result = self.save_blank_result()
        speaker = self.teams[0].speaker_set.first()
        self.assertRaises(TypeError, result.set_speaker, 'aff', 1, speaker)

    @incomplete_test
    def test_unfilled_debateteam(self, result):
        result.debateteams["aff"] = None

    @incomplete_test
    def test_unfilled_speaker(self, result):
        result.speakers["neg"][1] = None

    @bad_load_assertion_test
    def test_extraneous_debateteam(self, result):
        result.debateteams["test"] = None

    @bad_load_assertion_test
    def test_extraneous_team_in_speakers(self, result):
        result.speakers["test"] = None

    @bad_load_assertion_test
    def test_extraneous_team_in_ghosts(self, result):
        result.ghosts["test"] = True

    @bad_load_assertion_test
    def test_extraneous_speaker(self, result):
        result.speakers["aff"][5] = None

    @bad_load_assertion_test
    def test_extraneous_ghost(self, result):
        result.ghosts["aff"][5] = None


# ==============================================================================
# Actual test case classes
# ==============================================================================

class TestVotingDebateResultWithScores(GeneralSpeakerTestsMixin, BaseTestDebateResult):

    # Currently, the low-allowed and tie-allowed data aren't actually used, but
    # they are in place for future use, for when declared winners get fully
    # implemented.

    debate_result_class = DebateResultByAdjudicatorWithScores
    testdata = dict()

    testdata['high'] = { # standard high-point win
        'input': {
            'declared_winners': ['aff', 'neg', 'neg'],
            'scores': [[[75.0, 76.0, 74.0, 38.0], [76.0, 73.0, 75.0, 37.5]],
                       [[74.0, 75.0, 76.0, 37.0], [77.0, 74.0, 74.0, 38.0]],
                       [[75.0, 75.0, 75.0, 37.5], [76.0, 78.0, 77.0, 37.0]]]},
        'num_adjs': 3,
        'num_speakers_per_team': 3,
        'common': {
            'everyone_margins': [-1.66666666666667, 1.66666666666667],
            'everyone_scores': [[74.66666666666667, 75.33333333333333, 75.0, 37.5],
                                [76.33333333333333, 75.0, 75.33333333333333, 37.5]],
            'everyone_totals': [262.5, 264.16666666666663],
            'totals_by_adj': [[263.0, 261.5], [262.0, 263.0], [262.5, 268.0]]},
        'high-required': {
            'majority_adjs': [1, 2],
            'majority_margins': [-3.25, 3.25],
            'majority_scores': [[74.5, 75.0, 75.5, 37.25], [76.5, 76.0, 75.5, 37.5]],
            'majority_totals': [262.25, 265.5],
            'num_adjs_for_team': [1, 2],
            'sheets_valid': [True, True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['aff', 'neg', 'neg']},
        'low-allowed': {
            'majority_adjs': [1, 2],
            'majority_margins': [-3.25, 3.25],
            'majority_scores': [[74.5, 75.0, 75.5, 37.25], [76.5, 76.0, 75.5, 37.5]],
            'majority_totals': [262.25, 265.5],
            'num_adjs_for_team': [1, 2],
            'sheets_valid': [True, True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['aff', 'neg', 'neg']},
        'tied-allowed': {
            'majority_adjs': [1, 2],
            'majority_margins': [-3.25, 3.25],
            'majority_scores': [[74.5, 75.0, 75.5, 37.25], [76.5, 76.0, 75.5, 37.5]],
            'majority_totals': [262.25, 265.5],
            'num_adjs_for_team': [1, 2],
            'sheets_valid': [True, True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['aff', 'neg', 'neg']},
    }

    testdata['low'] = { # contains low-point wins that reverse the result
        'input': {
            'declared_winners': ['aff', 'aff', 'neg'],
            'scores': [[[73.0, 76.0, 79.0, 37.5], [77.0, 77.0, 78.0, 39.0]],
                       [[79.0, 80.0, 70.0, 36.0], [78.0, 79.0, 73.0, 37.0]],
                       [[73.0, 70.0, 77.0, 35.0], [76.0, 76.0, 77.0, 37.0]]]},
        'num_adjs': 3,
        'num_speakers_per_team': 3,
        'common': {
            'everyone_margins': [-6.166666666666686, 6.166666666666686],
            'everyone_scores': [[75.0, 75.33333333333333, 75.33333333333333, 36.166666666666664],
                                [77.0, 77.33333333333333, 76.0, 37.666666666666664]],
            'everyone_totals': [261.8333333333333, 268.0],
            'totals_by_adj': [[265.5, 271.0], [265.0, 267.0], [255.0, 266.0]]},
        'high-required': {
            'majority_adjs': [0, 1, 2],
            'majority_margins': [-6.166666666666686, 6.166666666666686],
            'majority_scores': [[75.0, 75.33333333333333, 75.33333333333333, 36.166666666666664],
                                [77.0, 77.33333333333333, 76.0, 37.666666666666664]],
            'majority_totals': [261.8333333333333, 268.0],
            'num_adjs_for_team': [0, 3],
            'sheets_valid': [True, True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg', 'neg', 'neg']},
        'low-allowed': {
            'majority_adjs': [0, 1],
            'majority_margins': [-3.75, 3.75],
            'majority_scores': [[76.0, 78.0, 74.5, 36.75], [77.5, 78.0, 75.5, 38.0]],
            'majority_totals': [265.25, 269.0],
            'num_adjs_for_team': [2, 1],
            'sheets_valid': [True, True, True],
            'valid': True,
            'winner': 'aff',
            'winner_by_adj': ['aff', 'aff', 'neg']},
        'tied-allowed': {
            'sheets_valid': [False, False, True],
            'valid': False,
            'winner_by_adj': [None, None, 'neg']},
    }

    testdata['tie'] = { # contains three tied-point wins
        'input': {
            'declared_winners': ['neg', 'aff', 'neg'],
            'scores': [[[73.0, 72.0, 78.0, 40.0], [73.0, 75.0, 75.0, 40.0]],
                      [[79.0, 73.0, 77.0, 39.5], [79.0, 75.0, 75.0, 39.5]],
                      [[75.0, 78.0, 77.0, 38.0], [72.0, 78.0, 80.0, 38.0]]]},
        'num_adjs': 3,
        'num_speakers_per_team': 3,
        'common': {
            'everyone_margins': [0.0, 0.0],
            'everyone_scores': [[75.66666666666667, 74.33333333333333, 77.33333333333333, 39.166666666666664],
                                [74.66666666666667, 76.0, 76.66666666666667, 39.166666666666664]],
            'everyone_totals': [266.5, 266.50000000000006],
            'totals_by_adj': [[263.0, 263.0], [268.5, 268.5], [268.0, 268.0]]},
        'high-required': {
            'sheets_valid': [False, False, False],
            'valid': False,
            'winner_by_adj': [None, None, None]},
        'low-allowed': {
            'majority_adjs': [0, 2],
            'majority_margins': [0.0, 0.0],
            'majority_scores': [[74.0, 75.0, 77.5, 39.0], [72.5, 76.5, 77.5, 39.0]],
            'majority_totals': [265.5, 265.5],
            'num_adjs_for_team': [1, 2],
            'sheets_valid': [True, True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg', 'aff', 'neg']},
        'tied-allowed': {
            'majority_adjs': [0, 2],
            'majority_margins': [0.0, 0.0],
            'majority_scores': [[74.0, 75.0, 77.5, 39.0], [72.5, 76.5, 77.5, 39.0]],
            'majority_totals': [265.5, 265.5],
            'num_adjs_for_team': [1, 2],
            'sheets_valid': [True, True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg', 'aff', 'neg']},
    }

    testdata['solo'] = {  # just one adjudicator
        'input': {
            'declared_winners': ['neg'],
            'scores': [[[74.0, 76.0, 37.5], [74.0, 77.0, 37.0]]]},
        'num_adjs': 1,
        'num_speakers_per_team': 2,
        'common': {
            'everyone_margins': [-0.5, 0.5],
            'everyone_scores': [[74.0, 76.0, 37.5], [74.0, 77.0, 37.0]],
            'everyone_totals': [187.5, 188.0],
            'totals_by_adj': [[187.5, 188.0]]},
        'high-required': {
            'majority_adjs': [0],
            'majority_margins': [-0.5, 0.5],
            'majority_scores': [[74.0, 76.0, 37.5], [74.0, 77.0, 37.0]],
            'majority_totals': [187.5, 188.0],
            'num_adjs_for_team': [0, 1],
            'sheets_valid': [True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg']},
        'low-allowed': {
            'majority_adjs': [0],
            'majority_margins': [-0.5, 0.5],
            'majority_scores': [[74.0, 76.0, 37.5], [74.0, 77.0, 37.0]],
            'majority_totals': [187.5, 188.0],
            'num_adjs_for_team': [0, 1],
            'sheets_valid': [True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg']},
        'tied-allowed': {
            'majority_adjs': [0],
            'majority_margins': [-0.5, 0.5],
            'majority_scores': [[74.0, 76.0, 37.5], [74.0, 77.0, 37.0]],
            'majority_totals': [187.5, 188.0],
            'num_adjs_for_team': [0, 1],
            'sheets_valid': [True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg']},
    }

    testdata['even'] = { # even panel, chair gets casting vote, note this is a low-point win
        'common': {
            'everyone_margins': [4.25, -4.25],
            'everyone_scores': [[80.0, 76.5, 36.5], [76.0, 73.5, 39.25]],
            'everyone_totals': [193.0, 188.75],
            'totals_by_adj': [[189.5, 194.0], [196.5, 183.5]]},
        'high-required': {
            'majority_adjs': [0],
            'majority_margins': [-4.5, 4.5],
            'majority_scores': [[80.0, 74.0, 35.5], [79.0, 76.0, 39.0]],
            'majority_totals': [189.5, 194.0],
            'num_adjs_for_team': [1, 1],
            'sheets_valid': [True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg', 'aff']},
        'input': {
            'declared_winners': ['neg', 'aff'],
            'scores': [[[80.0, 74.0, 35.5], [79.0, 76.0, 39.0]], [[80.0, 79.0, 37.5], [73.0, 71.0, 39.5]]]},
        'low-allowed': {
            'majority_adjs': [0],
            'majority_margins': [-4.5, 4.5],
            'majority_scores': [[80.0, 74.0, 35.5], [79.0, 76.0, 39.0]],
            'majority_totals': [189.5, 194.0],
            'num_adjs_for_team': [1, 1],
            'sheets_valid': [True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg', 'aff']},
        'num_adjs': 2,
        'num_speakers_per_team': 2,
        'tied-allowed': {
            'majority_adjs': [0],
            'majority_margins': [-4.5, 4.5],
            'majority_scores': [[80.0, 74.0, 35.5], [79.0, 76.0, 39.0]],
            'majority_totals': [189.5, 194.0],
            'num_adjs_for_team': [1, 1],
            'sheets_valid': [True, True],
            'valid': True,
            'winner': 'neg',
            'winner_by_adj': ['neg', 'aff']},
    }

    def save_scores_to_result(self, testdata, result):
        if result.uses_speakers:
            for adj, sheet in zip(self.adjs, testdata['input']['scores']):
                for side, teamscores in zip(self.SIDES, sheet):
                    for pos, score in enumerate(teamscores, start=1):
                        result.set_score(adj, side, pos, score)

        if result.uses_declared_winners:
            for adj, declared_winner in zip(self.adjs, testdata['input']['declared_winners']):
                result.add_winner(adj, declared_winner)

    # ==========================================================================
    # Normal operation
    # ==========================================================================

    @standard_test
    def test_totals_by_adj(self, result, testdata, scoresheet_type):
        for adj, totals in zip(self.adjs, testdata['common']['totals_by_adj']):
            for side, total in zip(self.SIDES, totals):
                self.assertEqual(total, result.scoresheets[adj].get_total(side))

    @standard_test
    def test_majority_adjudicators(self, result, testdata, scoresheet_type):
        majority = [self.adjs[i] for i in testdata[scoresheet_type]['majority_adjs']]
        with suppress_logs('results.result', logging.WARNING):
            self.assertCountEqual(majority, result.majority_adjudicators())

    @standard_test
    def test_individual_scores(self, result, testdata, scoresheet_type):
        for adj, sheet in zip(self.adjs, testdata['input']['scores']):
            for side, scores in zip(self.SIDES, sheet):
                for pos, score in enumerate(scores, start=1):
                    score_in_db = SpeakerScoreByAdj.objects.get(
                        ballot_submission__debate=self.debate,
                        ballot_submission__confirmed=True,
                        debate_team__side=side,
                        debate_adjudicator__adjudicator=adj,
                        position=pos).score
                    self.assertEqual(score, score_in_db)
                    self.assertEqual(score, result.get_score(adj, side, pos))

    @standard_test
    def test_winner_by_adj(self, result, testdata, scoresheet_type):
        for adj, winner in zip(self.adjs, testdata[scoresheet_type]['winner_by_adj']):
            if winner is None:
                self.assertEqual(len(result.scoresheets[adj].winners()), 0)
            else:
                self.assertEqual(result.get_winner(adj), winner)

    # --------------------------------------------------------------------------
    # Speaker scores
    # --------------------------------------------------------------------------

    @with_preference('scoring', 'margin_includes_dissenters', False)
    @standard_test
    def test_speaker_scores_majority(self, result, testdata, scoresheet_type):
        for side, totals in zip(self.SIDES, testdata[scoresheet_type]['majority_scores']):
            for pos, score in enumerate(totals, start=1):
                with suppress_logs('results.result', logging.WARNING):
                    self.assertAlmostEqual(score, self._get_speakerscore_in_db(side, pos).score)
                    self.assertAlmostEqual(score, result.speakerscore_field_score(side, pos))

    @with_preference('scoring', 'margin_includes_dissenters', True)
    @standard_test
    def test_speaker_scores_everyone(self, result, testdata, scoresheet_type):
        for side, totals in zip(self.SIDES, testdata['common']['everyone_scores']):
            for pos, score in enumerate(totals, start=1):
                with suppress_logs('results.result', logging.WARNING):
                    self.assertAlmostEqual(score, self._get_speakerscore_in_db(side, pos).score)
                    self.assertAlmostEqual(score, result.speakerscore_field_score(side, pos))

    # --------------------------------------------------------------------------
    # Team scores
    # --------------------------------------------------------------------------

    @standard_test
    def test_teamscore_field_points(self, result, testdata, scoresheet_type):
        for side in self.SIDES:
            points = 1 if side == testdata[scoresheet_type]['winner'] else 0
            with suppress_logs('results.result', logging.WARNING):
                self.assertEqual(points, self._get_teamscore_in_db(side).points)
                self.assertEqual(points, result.teamscore_field_points(side))

    @standard_test
    def test_teamscore_field_win(self, result, testdata, scoresheet_type):
        for side in self.SIDES:
            win = side == testdata[scoresheet_type]['winner']
            with suppress_logs('results.result', logging.WARNING):
                self.assertEqual(win, self._get_teamscore_in_db(side).win)
                self.assertEqual(win, result.teamscore_field_win(side))

    @with_preference('scoring', 'margin_includes_dissenters', False)
    @standard_test
    def test_teamscore_field_score_majority(self, result, testdata, scoresheet_type):
        for side, total in zip(self.SIDES, testdata[scoresheet_type]['majority_totals']):
            with suppress_logs('results.result', logging.WARNING):
                self.assertAlmostEqual(total, self._get_teamscore_in_db(side).score)
                self.assertAlmostEqual(total, result.teamscore_field_score(side))

    @with_preference('scoring', 'margin_includes_dissenters', False)
    @standard_test
    def test_teamscore_field_margin_majority(self, result, testdata, scoresheet_type):
        for side, margin in zip(self.SIDES, testdata[scoresheet_type]['majority_margins']):
            with suppress_logs('results.result', logging.WARNING):
                self.assertAlmostEqual(margin, self._get_teamscore_in_db(side).margin)
                self.assertAlmostEqual(margin, result.teamscore_field_margin(side))

    @with_preference('scoring', 'margin_includes_dissenters', True)
    @standard_test
    def test_teamscore_field_score_everyone(self, result, testdata, scoresheet_type):
        for side, total in zip(self.SIDES, testdata['common']['everyone_totals']):
            with suppress_logs('results.result', logging.WARNING):
                self.assertAlmostEqual(total, self._get_teamscore_in_db(side).score)
                self.assertAlmostEqual(total, result.teamscore_field_score(side))

    @with_preference('scoring', 'margin_includes_dissenters', True)
    @standard_test
    def test_teamscore_field_margin_everyone(self, result, testdata, scoresheet_type):
        for side, margin in zip(self.SIDES, testdata['common']['everyone_margins']):
            with suppress_logs('results.result', logging.WARNING):
                self.assertAlmostEqual(margin, self._get_teamscore_in_db(side).margin)
                self.assertAlmostEqual(margin, result.teamscore_field_margin(side))

    @standard_test
    def test_teamscore_field_votes_given(self, result, testdata, scoresheet_type):
        for side, votes in zip(self.SIDES, testdata[scoresheet_type]['num_adjs_for_team']):
            with suppress_logs('results.result', logging.WARNING):
                self.assertEqual(votes, self._get_teamscore_in_db(side).votes_given)
                self.assertEqual(votes, result.teamscore_field_votes_given(side))

    @standard_test
    def test_teamscore_field_votes_possible(self, result, testdata, scoresheet_type):
        nadjs = testdata['num_adjs']
        for side in self.SIDES:
            self.assertEqual(nadjs, self._get_teamscore_in_db(side).votes_possible)
            self.assertEqual(nadjs, result.teamscore_field_votes_possible(side))

    # ==========================================================================
    # Irregular operation
    # ==========================================================================

    @with_preference('scoring', 'margin_includes_dissenters', False)
    # @with_preference('scoring', 'scoresheet_type', 'high-required')
    def test_initially_unknown_sides(self):
        self._unset_sides()
        testdata = self.testdata['high']
        self.save_complete_result(testdata,
                post_create=lambda result: result.set_sides(*self.teams))
        result = self.get_result()

        # Just check a couple of fields
        winner = testdata['high-required']['winner']
        for side, margin in zip(self.SIDES, testdata['high-required']['majority_margins']):
            with suppress_logs('results.result', logging.WARNING):
                self.assertEqual(self._get_teamscore_in_db(side).win, side == winner)
                self.assertEqual(result.teamscore_field_win(side), side == winner)
                self.assertAlmostEqual(self._get_teamscore_in_db(side).margin, margin)
                self.assertAlmostEqual(result.teamscore_field_margin(side), margin)

    @incomplete_test
    def test_unfilled_scoresheet_score(self, result):
        result.scoresheets[self.adjs[0]].scores["aff"][1] = None

    @bad_load_assertion_test
    def test_extraneous_scoresheet(self, result):
        result.scoresheets["not-an-adj"] = None


class TestConsensusDebateResultWithScores(GeneralSpeakerTestsMixin, BaseTestDebateResult):

    debate_result_class = ConsensusDebateResultWithScores
    testdata = dict()

    testdata['high'] = {
        'declared_winner': 'aff',
        'scores': [[75.0, 76.0, 74.0, 38.0], [76.0, 73.0, 75.0, 37.5]],
        'num_adjs': 3,
        'num_speakers_per_team': 3,
        'totals': [263.0, 261.5],
        'margins': [1.5, -1.5],
        'high-required': {'valid': True, 'winner': 'aff'},
        'low-allowed': {'valid': True, 'winner': 'aff'},
        'tied-allowed': {'valid': True, 'winner': 'aff'},
    }

    testdata['low'] = { # contains low-point wins that reverse the result
        'declared_winners': 'aff',
        'scores': [[73.0, 76.0, 79.0, 37.5], [77.0, 77.0, 78.0, 39.0]],
        'num_adjs': 3,
        'num_speakers_per_team': 3,
        'totals': [265.5, 271.0],
        'margins': [-5.5, 5.5],
        'high-required': {'valid': True, 'winner': 'neg'},
        'low-allowed': {'valid': True, 'winner': 'aff'},
        'tied-allowed': {'valid': False, 'winner': None},
    }

    testdata['tie'] = { # contains low-point wins that reverse the result
        'declared_winners': 'neg',
        'scores': [[73.0, 72.0, 78.0, 40.0], [73.0, 75.0, 75.0, 40.0]],
        'num_adjs': 3,
        'num_speakers_per_team': 3,
        'totals': [263.0, 263.0],
        'margins': [0.0, 0.0],
        'high-required': {'valid': False, 'winner': None},
        'low-allowed': {'valid': True, 'winner': 'neg'},
        'tied-allowed': {'valid': True, 'winner': 'neg'},
    }

    testdata['two-speakers'] = {  # two speakers per team
        'declared_winners': 'neg',
        'scores': [[74.0, 76.0, 37.5], [74.0, 77.0, 37.0]],
        'num_adjs': 1,
        'num_speakers_per_team': 2,
        'totals': [187.5, 188.0],
        'margins': [-0.5, 0.5],
        'common': {
            'scores': [[74.0, 76.0, 37.5], [74.0, 77.0, 37.0]],
            'totals_by_adj': [[187.5, 188.0]]},
        'high-required': {'valid': True, 'winner': 'neg'},
        'low-allowed': {'valid': True, 'winner': 'neg'},
        'tied-allowed': {'valid': True, 'winner': 'neg'},
    }

    def save_scores_to_result(self, testdata, result):
        if result.uses_speakers:
            for side, teamscores in zip(self.SIDES, testdata['scores']):
                for pos, score in enumerate(teamscores, start=1):
                    result.set_score(side, pos, score)

        if result.uses_declared_winners:
            result.add_winner(testdata['declared_winner'])

    # ==========================================================================
    # Normal operation
    # ==========================================================================

    @standard_test
    def test_save(self, result, testdata, scoresheet_type):
        # Run self.save_complete_result and check completeness
        self.assertTrue(result.is_complete())

    @standard_test
    def test_speaker_scores(self, result, testdata, scoresheet_type):
        for side, totals in zip(self.SIDES, testdata['scores']):
            for pos, score in enumerate(totals, start=1):
                self.assertAlmostEqual(score, self._get_speakerscore_in_db(side, pos).score)
                self.assertAlmostEqual(score, result.speakerscore_field_score(side, pos))

    @standard_test
    def test_teamscore_field_points(self, result, testdata, scoresheet_type):
        for side in self.SIDES:
            points = 1 if side == testdata[scoresheet_type]['winner'] else 0
            self.assertEqual(points, self._get_teamscore_in_db(side).points)
            self.assertEqual(points, result.teamscore_field_points(side))

    @standard_test
    def test_teamscore_field_win(self, result, testdata, scoresheet_type):
        for side in self.SIDES:
            win = side == testdata[scoresheet_type]['winner']
            self.assertEqual(win, self._get_teamscore_in_db(side).win)
            self.assertEqual(win, result.teamscore_field_win(side))

    @standard_test
    def test_teamscore_field_score(self, result, testdata, scoresheet_type):
        for side, total in zip(self.SIDES, testdata['totals']):
            self.assertAlmostEqual(total, self._get_teamscore_in_db(side).score)
            self.assertAlmostEqual(total, result.teamscore_field_score(side))

    @standard_test
    def test_teamscore_field_margin(self, result, testdata, scoresheet_type):
        for side, margin in zip(self.SIDES, testdata['margins']):
            self.assertAlmostEqual(margin, self._get_teamscore_in_db(side).margin)
            self.assertAlmostEqual(margin, result.teamscore_field_margin(side))

    @standard_test
    def test_teamscore_field_blank_fields(self, result, testdata, scoresheet_type):
        for side in self.SIDES:
            self.assertIsNone(self._get_teamscore_in_db(side).votes_given)
            self.assertIsNone(self._get_teamscore_in_db(side).votes_possible)

    # ==========================================================================
    # Irregular operation
    # ==========================================================================

    # @with_preference('scoring', 'scoresheet_type', 'high-required')
    def test_initially_unknown_sides(self):
        self._unset_sides()
        testdata = self.testdata['high']
        self.save_complete_result(testdata,
                post_create=lambda result: result.set_sides(*self.teams))
        result = self.get_result()

        # Just check a couple of fields
        winner = testdata['high-required']['winner']
        for side, margin in zip(self.SIDES, testdata['margins']):
            self.assertEqual(self._get_teamscore_in_db(side).win, side == winner)
            self.assertEqual(result.teamscore_field_win(side), side == winner)
            self.assertAlmostEqual(self._get_teamscore_in_db(side).margin, margin)
            self.assertAlmostEqual(result.teamscore_field_margin(side), margin)

    @incomplete_test
    def test_unfilled_scoresheet_score(self, result):
        result.scoresheet.scores["aff"][1] = None
