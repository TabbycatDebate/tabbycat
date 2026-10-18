import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from results.models import BallotSubmission
from tournaments.models import Tournament
from utils.misc import reverse_tournament


class DashboardBallotTests(TestCase):

    fixtures = ['after_round_4.json']

    def setUp(self):
        self.tournament = Tournament.objects.first()
        self.round = self.tournament.current_round
        self.ballots = list(BallotSubmission.objects.filter(
            debate__round=self.round, confirmed=True,
        ).order_by('pk'))
        timestamp = timezone.now()
        for index, ballot in enumerate(self.ballots):
            BallotSubmission.objects.filter(pk=ballot.pk).update(
                timestamp=timestamp + timedelta(seconds=index),
            )
        self.expected_ids = [ballot.pk for ballot in reversed(self.ballots[-10:])]
        user = get_user_model().objects.create_user('dashboard-admin', is_superuser=True)
        self.client.force_login(user)
        self.url = reverse_tournament('tournament-admin-home', self.tournament)

    def get_ballots(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        return json.loads(response.context['initialBallots'])

    def get_ballots_with_concurrent_change(self, change):
        changed = False

        def execute(execute, sql, params, many, context):
            nonlocal changed
            result = execute(sql, params, many, context)
            if not changed and 'results_ballotsubmission' in sql and 'LIMIT 10' in sql:
                # Interleave a write after the recent-results SELECT, before
                # subsequent queries can reselect debates or confirmed ballots.
                changed = True
                change()
            return result

        with connection.execute_wrapper(execute):
            ballots = self.get_ballots()
        self.assertTrue(changed, 'The recent-results query was not intercepted')
        return ballots

    def test_latest_ten_confirmed_ballots_in_current_round(self):
        self.assertEqual([ballot['id'] for ballot in self.get_ballots()], self.expected_ids)

    def test_no_confirmed_ballots(self):
        BallotSubmission.objects.filter(debate__round=self.round).update(confirmed=False)

        self.assertEqual(self.get_ballots(), [])

    def test_confirmation_during_loading_keeps_selected_ballots(self):
        incoming = self.ballots[0]
        BallotSubmission.objects.filter(pk=incoming.pk).update(
            confirmed=False, timestamp=timezone.now() + timedelta(days=1),
        )

        ballots = self.get_ballots_with_concurrent_change(
            lambda: BallotSubmission.objects.filter(pk=incoming.pk).update(confirmed=True),
        )

        self.assertEqual([ballot['id'] for ballot in ballots], self.expected_ids)
        self.assertEqual(self.get_ballots()[0]['id'], incoming.pk)

    def test_unconfirmation_during_loading_keeps_selected_ballots(self):
        outgoing_id = self.expected_ids[0]

        ballots = self.get_ballots_with_concurrent_change(
            lambda: BallotSubmission.objects.filter(pk=outgoing_id).update(confirmed=False),
        )

        self.assertEqual([ballot['id'] for ballot in ballots], self.expected_ids)
        self.assertTrue(ballots[0]['confirmed'])
        self.assertNotIn(outgoing_id, [ballot['id'] for ballot in self.get_ballots()])
