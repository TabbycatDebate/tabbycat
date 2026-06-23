import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from participants.models import Institution, Team
from tournaments.models import Round, Tournament
from utils.misc import reverse_tournament

from ..models import N1RuleFinePayment


class N1RuleViewsTest(TestCase):
    """Smoke tests: admin can load the N-1 rule GET views."""
    fixtures = ['after_round_4.json']

    def setUp(self):
        super().setUp()
        self.tournament = Tournament.objects.first()
        user, _ = get_user_model().objects.get_or_create(username='test_admin', is_superuser=True)
        self.client.force_login(user)

    def test_assignments_view_loads(self):
        url = reverse_tournament('adjallocation-n1rule-assignments', self.tournament)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_status_view_loads(self):
        url = reverse_tournament('adjallocation-n1rule-status', self.tournament)
        self.assertEqual(self.client.get(url).status_code, 200)


class N1RuleFinePaymentViewTest(TestCase):

    def setUp(self):
        super().setUp()
        self.tournament = Tournament.objects.create(slug='t', name='T')
        Round.objects.create(tournament=self.tournament, seq=1, name='R1')
        self.institution = Institution.objects.create(code='INS', name='Test Institution')
        self.team = Team.objects.create(tournament=self.tournament, reference='T1')
        self.url = reverse_tournament('adjallocation-n1rule-fines', self.tournament)
        user = get_user_model().objects.create(username='admin', is_superuser=True)
        self.client.force_login(user)

    def _post(self, data):
        return self.client.post(self.url, json.dumps(data), content_type='application/json')

    def test_unauthenticated_redirects(self):
        self.client.logout()
        response = self._post({'institution_id': self.institution.pk, 'fines_paid': 1})
        self.assertIn(response.status_code, [302, 403])

    def test_post_institution_creates_record(self):
        response = self._post({'institution_id': self.institution.pk, 'fines_paid': 3})
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['fines_paid'], 3)
        record = N1RuleFinePayment.objects.get(tournament=self.tournament, institution=self.institution)
        self.assertEqual(record.fines_paid, 3)

    def test_post_institution_updates_existing(self):
        N1RuleFinePayment.objects.create(
            tournament=self.tournament, institution=self.institution, fines_paid=1,
        )
        response = self._post({'institution_id': self.institution.pk, 'fines_paid': 5})
        self.assertEqual(response.status_code, 200)
        record = N1RuleFinePayment.objects.get(tournament=self.tournament, institution=self.institution)
        self.assertEqual(record.fines_paid, 5)
        self.assertEqual(N1RuleFinePayment.objects.filter(tournament=self.tournament).count(), 1)

    def test_post_team_creates_record(self):
        response = self._post({'team_id': self.team.pk, 'fines_paid': 1})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['ok'])
        record = N1RuleFinePayment.objects.get(tournament=self.tournament, team=self.team)
        self.assertEqual(record.fines_paid, 1)

    def test_negative_fines_clamped_to_zero(self):
        response = self._post({'institution_id': self.institution.pk, 'fines_paid': -5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['fines_paid'], 0)

    def test_missing_target_returns_400(self):
        response = self._post({'fines_paid': 1})
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_returns_400(self):
        response = self.client.post(self.url, 'not-json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_fines_value_returns_400(self):
        response = self._post({'institution_id': self.institution.pk, 'fines_paid': 'abc'})
        self.assertEqual(response.status_code, 400)


class N1RuleFinePaymentModelTest(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(slug='t', name='T')
        self.institution = Institution.objects.create(code='INS', name='Test Institution')
        self.team = Team.objects.create(tournament=self.tournament, reference='T1')

    def test_str_institution(self):
        fp = N1RuleFinePayment(tournament=self.tournament, institution=self.institution, fines_paid=2)
        self.assertIn('2', str(fp))
        self.assertIn('Test Institution', str(fp))

    def test_str_team(self):
        fp = N1RuleFinePayment(tournament=self.tournament, team=self.team, fines_paid=1)
        self.assertIn('1', str(fp))

    def test_default_fines_paid_is_zero(self):
        fp = N1RuleFinePayment.objects.create(tournament=self.tournament, institution=self.institution)
        self.assertEqual(fp.fines_paid, 0)