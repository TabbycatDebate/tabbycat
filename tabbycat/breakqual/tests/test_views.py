import json
import logging

from django.contrib.auth import get_user_model
from django.test import TestCase

from breakqual.models import BreakingTeam
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


class AdminBreakingTeamsViewTest(CompletedTournamentTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.admin = get_user_model().objects.create(username='break_admin', is_superuser=True)
        self.client.force_login(self.admin)

    def test_remark_column_uses_form_select_cells(self):
        category = self.tournament.breakcategory_set.get(slug='open')
        breaking_team = category.breakingteam_set.first()
        breaking_team.remark = BreakingTeam.Remark.CAPPED
        breaking_team.save()
        response = self.client.get(self.reverse_url('breakqual-teams', category=category.slug))
        self.assertResponseOK(response)

        table = json.loads(response.context['tables_data'])[0]
        remark_index = [header['key'] for header in table['head']].index('edit-remark')
        cells = [row[remark_index] for row in table['data']]

        self.assertTrue(cells)
        self.assertTrue(all(cell['component'] == 'ajax-select-cell' for cell in cells))
        self.assertTrue(all(cell['noSave'] for cell in cells))
        self.assertTrue(all(cell['name'].startswith('remark_') for cell in cells))
        self.assertTrue(all('text' not in cell for cell in cells))
        selected_cell = next(cell for cell in cells if cell['name'] == f'remark_{breaking_team.team_id}')
        self.assertEqual(selected_cell['value'], BreakingTeam.Remark.CAPPED)


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
