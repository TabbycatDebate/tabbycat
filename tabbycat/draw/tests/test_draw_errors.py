import logging
from html import unescape

from django.contrib.messages import ERROR

from availability.utils import set_availability
from draw.generator import DrawUserError
from draw.generator.common import DrawOptionError
from draw.models import TeamSideAllocation
from draw.types import DebateSide
from options.models import TournamentPreferenceModel
from options.serializers import MultiValueSerializer
from standings.base import StandingsError
from tournaments.models import Round
from utils.misc import reverse_round
from utils.tests import suppress_logs, TournamentTestCase


class TestCreateDrawViewErrors(TournamentTestCase):

    fixtures = ['after_round_1.json']
    round_seq = 2

    def setUp(self):
        super().setUp()
        self.client.login(username="admin", password="admin")
        self.round = self.tournament.round_set.get(seq=self.round_seq)
        self.tournament.preferences['standings__team_standings_precedence'] = ['wins', 'speaks_sum']

    def run_test_for_error_response(self, expected_loglevel, error_type):
        url = self.reverse_round('draw-create')
        with self.assertLogs('draw.views', level=expected_loglevel) as cm, \
                suppress_logs('standings.metrics', logging.INFO):
            response = self.client.post(url, follow=True)

        # Check that it logged something at the correct level (WARNING or ERROR), depending on the error
        self.assertEqual(cm.records[0].levelno, expected_loglevel)
        self.assertEqual(cm.records[0].exc_info[0], error_type)

        # Check that it redirects appropriately
        self.assertRedirects(response, self.reverse_round('availability-index'))

        # Check that there is a message at level ERROR
        messages = response.context.get('messages', [])
        self.assertEqual(len(messages), 1)
        message = list(messages)[0]
        self.assertEqual(message.level, ERROR)
        return str(message)

    def reverse_round(self, view_name):
        return reverse_round(view_name, self.round)

    def test_no_teams(self):
        set_availability(self.tournament.team_set.none(), self.round)
        self.run_test_for_error_response(logging.WARNING, DrawUserError)

    def test_odd_teams(self):
        set_availability(self.tournament.team_set.all()[:23], self.round)
        self.run_test_for_error_response(logging.WARNING, DrawUserError)

    def test_power_pairing_with_preallocated_sides_and_bracket_penalty(self):
        self.tournament.preferences['draw_rules__draw_side_allocations'] = 'preallocated'
        self.tournament.preferences['draw_rules__draw_avoid_conflicts'] = 'off'
        self.tournament.preferences['draw_rules__draw_odd_bracket'] = 'intermediate1'
        self.tournament.preferences['draw_rules__draw_bracket_penalty'] = 10
        set_availability(self.tournament.team_set.all(), self.round)
        teams = list(self.round.active_teams.order_by('pk'))
        TeamSideAllocation.objects.bulk_create(
            TeamSideAllocation(round=self.round, team=team, side=DebateSide.NEG if i % 2 else DebateSide.AFF)
            for i, team in enumerate(teams)
        )

        response = self.client.post(self.reverse_round('draw-create'))

        self.assertRedirects(response, self.reverse_round('draw'), fetch_redirect_response=False)
        self.round.refresh_from_db()
        self.assertEqual(self.round.draw_status, Round.Status.DRAFT)
        self.assertEqual(self.round.debate_set.count(), len(teams) // 2)

    def test_incompatible_odd_bracket_option(self):
        self.tournament.preferences['draw_rules__draw_side_allocations'] = 'balance'
        self.tournament.preferences['draw_rules__draw_avoid_conflicts'] = 'one_up_one_down'
        self.tournament.preferences['draw_rules__draw_odd_bracket'] = 'intermediate1'
        set_availability(self.tournament.team_set.all(), self.round)

        message = self.run_test_for_error_response(logging.WARNING, DrawOptionError)
        self.assertIn("does not support intermediate1 for odd_bracket", message)
        self.assertIn("pullup_top", message)
        self.assertIn("draw rules</a>", message)
        self.assertFalse(self.round.debate_set.exists())

    def test_bad_standings(self):
        TournamentPreferenceModel.objects.update_or_create(instance=self.tournament, section='standings',
                name='team_standings_precedence',
                defaults={'raw_value': MultiValueSerializer.separator.join(['wins', 'speaks_sum', 'wins'])})
        self.run_test_for_error_response(logging.ERROR, StandingsError)
        TournamentPreferenceModel.objects.update_or_create(instance=self.tournament, section='standings',
                name='team_standings_precedence',
                defaults={'raw_value': MultiValueSerializer.separator.join(['wins', 'speaks_sum'])})

    def test_elim_progress_in_power_paired_precedence(self):
        self.tournament.preferences['standings__team_standings_precedence'] = [
            'elim_progress', 'wins', 'speaks_sum',
        ]

        message = self.run_test_for_error_response(logging.WARNING, DrawUserError)

        self.assertIn("Power-paired draws can't be generated when elimination", unescape(message))
