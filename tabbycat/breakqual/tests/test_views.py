import json
import logging

from django.test import TestCase

from draw.models import Debate
from results.models import BallotSubmission, TeamScore
from utils.tests import CompletedTournamentTestMixin, ConditionalTableViewTestsMixin, suppress_logs


class BreakingTeamsViewTestMixin(ConditionalTableViewTestsMixin):
    view_name = 'breakqual-public-teams'
    view_toggle_preference = 'public_features__public_breaking_teams'

    def get_view_reverse_kwargs(self):
        kwargs = super().get_view_reverse_kwargs()
        kwargs['category'] = self.break_category_slug
        return kwargs

    def expected_row_counts(self):
        category = self.tournament.breakcategory_set.get(slug=self.break_category_slug)
        return [category.breaking_teams.count()]

    def test_view_enabled(self):
        # Suppress standings queryset info logging
        with suppress_logs('standings.metrics', logging.INFO):
            super().test_view_enabled()


class PublicOpenBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_category_slug = 'open'


class PublicESLBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_category_slug = 'esl'


class PublicNoviceBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_category_slug = 'novice'


class PublicBreakingAdjudicatorsViewTest(ConditionalTableViewTestsMixin, TestCase):
    view_name = 'breakqual-public-adjs'
    view_toggle_preference = 'public_features__public_breaking_adjs'

    def expected_row_counts(self):
        return [self.tournament.adjudicator_set.filter(breaking=True).count()]


class PublicEliminationBracketViewTest(CompletedTournamentTestMixin, TestCase):
    fixtures = ['before_oqf_ssf.json']

    def setUp(self):
        super().setUp()
        self.tournament.preferences['public_features__public_results'] = True
        self.tournament.preferences['public_features__public_breaking_teams'] = True

        self.round = self.tournament.round_set.get(abbreviation='OQF')
        self.debate = self.round.debate_set.order_by('room_rank').first()
        self.debate.result_status = Debate.STATUS_CONFIRMED
        self.debate.save()

        ballot = BallotSubmission.objects.create(debate=self.debate, confirmed=True)
        for index, debate_team in enumerate(self.debate.debateteam_set.order_by('side')):
            TeamScore.objects.create(
                ballot_submission=ballot,
                debate_team=debate_team,
                win=index == 0,
            )

    def get_bracket_data(self):
        response = self.get_response('breakqual-public-bracket', category='open')
        self.assertResponseOK(response)
        return json.loads(response.context['bracket_data'])

    def get_oqf_data(self):
        return next(round_data for round_data in self.get_bracket_data()['rounds'] if round_data['seq'] == self.round.seq)

    def test_unreleased_silent_round_is_hidden(self):
        self.assertIsNone(self.get_oqf_data()['pairings'])

    def test_all_results_released_shows_teams_and_results(self):
        self.tournament.preferences['tab_release__all_results_released'] = True

        round_data = self.get_oqf_data()
        pairing = next(pairing for pairing in round_data['pairings'] if pairing['room_rank'] == self.debate.room_rank)

        self.assertEqual(len(pairing['teams']), self.debate.debateteam_set.count())
        self.assertEqual([team['advancing'] for team in pairing['teams']], [True, False])
