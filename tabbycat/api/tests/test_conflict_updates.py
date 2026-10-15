from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APITestCase

from participants.models import Adjudicator, Institution, Team
from tournaments.models import Tournament
from utils.misc import reverse_tournament

User = get_user_model()


class ConflictUpdateTests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(User.objects.create_superuser(username='admin', password='admin'))
        self.tournament = Tournament.objects.create(slug='conflicts')
        self.team = Team.objects.create(tournament=self.tournament, reference='Team')
        self.adjudicator = Adjudicator.objects.create(tournament=self.tournament, name='Judge')
        self.institutions = [Institution.objects.create(name=name, code=name) for name in ['Old', 'Keep', 'New']]
        teams = [Team.objects.create(tournament=self.tournament, reference=name) for name in ['Old', 'Keep', 'New']]
        adjudicators = [Adjudicator.objects.create(tournament=self.tournament, name=name) for name in ['Old', 'Keep', 'New']]
        self.cases = [
            (self.team, 'api-team-detail', 'institution_conflicts', self.institutions, 'api-global-institution-detail'),
            (self.adjudicator, 'api-adjudicator-detail', 'institution_conflicts', self.institutions, 'api-global-institution-detail'),
            (self.adjudicator, 'api-adjudicator-detail', 'team_conflicts', teams, 'api-team-detail'),
            (self.adjudicator, 'api-adjudicator-detail', 'adjudicator_conflicts', adjudicators, 'api-adjudicator-detail'),
        ]

    def link(self, endpoint, obj):
        if endpoint == 'api-global-institution-detail':
            return reverse(endpoint, kwargs={'pk': obj.pk})
        return reverse_tournament(endpoint, self.tournament, kwargs={'pk': obj.pk})

    def test_explicit_add_remove_and_retries(self):
        for participant, endpoint, name, objects, related_endpoint in self.cases:
            with self.subTest(model=type(participant).__name__, field=name):
                old, keep, new = objects
                relation = getattr(participant, name)
                relation.set([old, keep])
                data = {name: [self.link(related_endpoint, new)], 'delete_' + name: [self.link(related_endpoint, old)]}
                for attempt in range(2):
                    response = self.client.patch(self.link(endpoint, participant), data)
                    self.assertEqual(response.status_code, 200, response.data)
                    self.assertNotIn('delete_' + name, response.data)
                    participant.refresh_from_db()
                    self.assertEqual(set(getattr(participant, name).all()), {keep, new})
                response = self.client.patch(self.link(endpoint, participant), {'delete_' + name: []})
                self.assertEqual(response.status_code, 200, response.data)
                participant.refresh_from_db()
                self.assertEqual(set(getattr(participant, name).all()), {keep, new})

    def test_deletion_without_additions_and_invalid_requests(self):
        for participant, endpoint, name, objects, related_endpoint in self.cases:
            with self.subTest(model=type(participant).__name__, field=name):
                old, keep, new = objects
                relation = getattr(participant, name)
                relation.set([old, keep])
                old_url = self.link(related_endpoint, old)
                url = self.link(endpoint, participant)
                response = self.client.patch(url, {name: [old_url], 'delete_' + name: [old_url]})
                self.assertEqual(response.status_code, 400)
                missing_url = old_url.rsplit('/', 1)[0] + '/999999999'
                response = self.client.patch(url, {name: [self.link(related_endpoint, new)], 'delete_' + name: [missing_url]})
                self.assertEqual(response.status_code, 400)
                participant.refresh_from_db()
                self.assertEqual(set(getattr(participant, name).all()), {old, keep})
                response = self.client.patch(url, {'delete_' + name: [old_url, self.link(related_endpoint, new)]})
                self.assertEqual(response.status_code, 200, response.data)
                participant.refresh_from_db()
                self.assertEqual(set(getattr(participant, name).all()), {keep})

    def test_reject_deletion_on_post(self):
        url = self.link('api-team-detail', self.team)
        response = self.client.post(url, {'reference': 'Team', 'delete_institution_conflicts': []})
        self.assertEqual(response.status_code, 400)
        self.assertIn('delete_institution_conflicts', response.data)
        response = self.client.post(reverse_tournament('api-team-list', self.tournament), {'reference': 'Created', 'delete_institution_conflicts': []})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Team.objects.filter(reference='Created').exists())

    def test_cross_tournament_and_unauthorized_deletion(self):
        other = Tournament.objects.create(slug='other')
        team = Team.objects.create(tournament=other, reference='Other')
        url = self.link('api-adjudicator-detail', self.adjudicator)
        response = self.client.patch(url, {'delete_team_conflicts': [reverse_tournament('api-team-detail', other, kwargs={'pk': team.pk})]})
        self.assertEqual(response.status_code, 400)
        self.adjudicator.team_conflicts.add(self.team)
        self.client.force_authenticate(user=None)
        response = self.client.patch(url, {'delete_team_conflicts': [self.link('api-team-detail', self.team)]})
        self.assertIn(response.status_code, [401, 403])
        self.assertTrue(self.adjudicator.team_conflicts.filter(pk=self.team.pk).exists())

    def test_conflict_changes_roll_back_if_participant_save_fails(self):
        old, keep, new = self.institutions
        self.team.institution_conflicts.set([old, keep])
        data = {
            'institution_conflicts': [self.link('api-global-institution-detail', new)],
            'delete_institution_conflicts': [self.link('api-global-institution-detail', old)],
        }
        with patch.object(Team, 'save', side_effect=RuntimeError('save failed')), self.assertLogs('api.exceptions', level='ERROR'):
            response = self.client.patch(self.link('api-team-detail', self.team), data)
        self.assertEqual(response.status_code, 500)
        self.team.refresh_from_db()
        self.assertEqual(set(self.team.institution_conflicts.all()), {old, keep})

    def test_schema_documents_write_only_deletion_lists(self):
        schema = SchemaGenerator().get_schema(request=None, public=True)
        for component, names in [('PatchedTeam', ['institution_conflicts']), ('PatchedAdjudicator', ['institution_conflicts', 'team_conflicts', 'adjudicator_conflicts'])]:
            for name in names:
                field = schema['components']['schemas'][component]['properties']['delete_' + name]
                self.assertEqual(field['type'], 'array')
                self.assertTrue(field['writeOnly'])
                self.assertNotIn('description', field)
                self.assertEqual(schema['components']['schemas'][component]['properties'][name]['description'], 'Merges into existing conflicts')
        response = self.client.get(reverse('api-schema'), HTTP_ACCEPT='application/vnd.oai.openapi+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('delete_institution_conflicts', response.content.decode())
        response = self.client.get(reverse('redoc'))
        self.assertEqual(response.status_code, 200)
