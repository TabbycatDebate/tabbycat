from itertools import product
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase

from participants.models import Adjudicator, Institution, Team
from tournaments.models import Tournament
from utils.misc import reverse_tournament
from venues.models import VenueCategory

from ..serializers import AdjudicatorSerializer, PerTournamentInstitutionSerializer, TeamSerializer

User = get_user_model()


class RelationshipUpdateTests(APITestCase):
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
        self.categories = [VenueCategory.objects.create(tournament=self.tournament, name=name) for name in ['Old', 'Keep', 'New']]
        self.venue_cases = [(self.team, 'api-team-detail'), (self.adjudicator, 'api-adjudicator-detail'), (self.institutions[0], 'api-global-institution-detail')]

    def link(self, endpoint, obj):
        if endpoint == 'api-global-institution-detail':
            return reverse(endpoint, kwargs={'pk': obj.pk})
        return reverse_tournament(endpoint, self.tournament, kwargs={'pk': obj.pk})

    def assert_conflicts(self, response, participant, name, expected, status=200):
        self.assertEqual(response.status_code, status, response.data)
        if status == 200:
            self.assertNotIn('remove_' + name, response.data)
        participant.refresh_from_db()
        self.assertEqual(set(getattr(participant, name).all()), expected)

    def test_institution_changes_preserve_existing_conflicts(self):
        old, unrelated, new = self.institutions
        supplied = Institution.objects.create(name='Supplied', code='Supplied')
        for participant, endpoint, name, objects, related_endpoint in self.cases[:2]:
            fields = {'reference': 'Team'} if isinstance(participant, Team) else {'name': 'Judge', 'team_conflicts': [], 'adjudicator_conflicts': []}
            for method, institution, conflicts in product(['patch', 'post'], [old, new, None, 'omitted'], ['omitted', [], [old, supplied]]):
                with self.subTest(model=type(participant).__name__, method=method, institution=institution, conflicts=conflicts):
                    participant.institution = old
                    participant.save()
                    participant.institution_conflicts.set([old, unrelated])
                    data = dict(fields)
                    if institution != 'omitted':
                        data['institution'] = self.link(related_endpoint, institution) if institution else None
                    if conflicts != 'omitted':
                        data[name] = [self.link(related_endpoint, obj) for obj in conflicts]
                    expected = {old, unrelated} if method == 'patch' or conflicts == 'omitted' else set(conflicts)
                    if method == 'patch' and conflicts != 'omitted':
                        expected.update(conflicts)
                    invalid = isinstance(participant, Adjudicator) and method == 'post' and (institution == 'omitted' or conflicts == 'omitted')
                    response = getattr(self.client, method)(self.link(endpoint, participant), data)
                    self.assert_conflicts(response, participant, name, {old, unrelated} if invalid else expected, status=400 if invalid else 200)
                    self.assertEqual(participant.institution, old if invalid or institution == 'omitted' else institution)

    def test_explicit_add_remove_and_retries(self):
        for participant, endpoint, name, objects, related_endpoint in self.cases:
            with self.subTest(model=type(participant).__name__, field=name):
                old, keep, new = objects
                relation = getattr(participant, name)
                relation.set([old, keep])
                data = {name: [self.link(related_endpoint, new)], 'remove_' + name: [self.link(related_endpoint, old)]}
                for payload in [data, data, {'remove_' + name: []}]:
                    self.assert_conflicts(self.client.patch(self.link(endpoint, participant), payload), participant, name, {keep, new})

    def test_removal_without_additions_and_invalid_requests(self):
        for participant, endpoint, name, objects, related_endpoint in self.cases:
            with self.subTest(model=type(participant).__name__, field=name):
                old, keep, new = objects
                relation = getattr(participant, name)
                relation.set([old, keep])
                old_url = self.link(related_endpoint, old)
                url = self.link(endpoint, participant)
                response = self.client.patch(url, {name: [old_url], 'remove_' + name: [old_url]})
                self.assert_conflicts(response, participant, name, {old, keep}, status=400)
                missing_url = old_url.rsplit('/', 1)[0] + '/999999999'
                response = self.client.patch(url, {name: [self.link(related_endpoint, new)], 'remove_' + name: [missing_url]})
                self.assert_conflicts(response, participant, name, {old, keep}, status=400)
                response = self.client.patch(url, {'remove_' + name: [old_url, self.link(related_endpoint, new)]})
                self.assert_conflicts(response, participant, name, {keep})

    def test_reject_removal_on_post(self):
        for name in ['remove_institution_conflicts', 'remove_venue_constraints']:
            for url in [self.link('api-team-detail', self.team), reverse_tournament('api-team-list', self.tournament)]:
                response = self.client.post(url, {'reference': 'Created', name: []})
                self.assertEqual(response.status_code, 400)
                self.assertIn(name, response.data)
                self.assertFalse(Team.objects.filter(reference='Created').exists())

    def test_cross_tournament_and_unauthorized_removal(self):
        other = Tournament.objects.create(slug='other')
        team = Team.objects.create(tournament=other, reference='Other')
        url = self.link('api-adjudicator-detail', self.adjudicator)
        response = self.client.patch(url, {'remove_team_conflicts': [reverse_tournament('api-team-detail', other, kwargs={'pk': team.pk})]})
        self.assertEqual(response.status_code, 400)
        self.adjudicator.team_conflicts.add(self.team)
        self.client.force_authenticate(user=None)
        response = self.client.patch(url, {'remove_team_conflicts': [self.link('api-team-detail', self.team)]})
        self.assertIn(response.status_code, [401, 403])
        self.assertTrue(self.adjudicator.team_conflicts.filter(pk=self.team.pk).exists())

    def test_conflict_changes_roll_back_if_participant_save_fails(self):
        old, keep, new = self.institutions
        self.team.institution_conflicts.set([old, keep])
        data = {
            'institution_conflicts': [self.link('api-global-institution-detail', new)],
            'remove_institution_conflicts': [self.link('api-global-institution-detail', old)],
        }
        with patch.object(Team, 'save', side_effect=RuntimeError('save failed')), self.assertLogs('api.exceptions', level='ERROR'):
            response = self.client.patch(self.link('api-team-detail', self.team), data)
        self.assert_conflicts(response, self.team, 'institution_conflicts', {old, keep}, status=500)

    def test_schema_documents_write_only_removal_lists(self):
        response = self.client.get(reverse('api-schema'), HTTP_ACCEPT='application/vnd.oai.openapi+json')
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        for component, names in [('PatchedTeam', ['institution_conflicts']), ('PatchedAdjudicator', ['institution_conflicts', 'team_conflicts', 'adjudicator_conflicts'])]:
            for name in names:
                field = schema['components']['schemas'][component]['properties']['remove_' + name]
                self.assertEqual(field['type'], 'array')
                self.assertTrue(field['writeOnly'])
                self.assertEqual(field['description'], f"Remove these {name.removesuffix('_conflicts')} conflicts. Missing conflicts are ignored. Only available on PATCH")
                self.assertEqual(schema['components']['schemas'][component]['properties'][name]['description'], 'Merges into existing conflicts')
        for component in ['PatchedTeam', 'PatchedAdjudicator', 'PatchedInstitution']:
            field = schema['components']['schemas'][component]['properties']['remove_venue_constraints']
            self.assertEqual(field['type'], 'array')
            self.assertEqual(field['items']['format'], 'uri')
            self.assertTrue(field['writeOnly'])
        response = self.client.get(reverse('redoc'))
        self.assertEqual(response.status_code, 200)

    def test_venue_constraint_removal_and_retries(self):
        old, keep, new = self.categories
        for participant, endpoint in self.venue_cases:
            with self.subTest(model=type(participant).__name__):
                for category, priority in [(old, 1), (old, 2), (keep, 3)]:
                    participant.venue_constraints.create(category=category, priority=priority)
                url = self.link(endpoint, participant)
                removal = {'remove_venue_constraints': [self.link('api-venuecategory-detail', old)]}
                addition = {'venue_constraints': [{'category': self.link('api-venuecategory-detail', new), 'priority': 4}]}
                for payload in [dict(removal, **addition), removal, {'remove_venue_constraints': []}, {}]:
                    response = self.client.patch(url, payload)
                    self.assertEqual(response.status_code, 200, response.data)
                    self.assertNotIn('remove_venue_constraints', response.data)
                    self.assertEqual(sorted(row['priority'] for row in response.data['venue_constraints']), [3, 4])
                    self.assertEqual(set(participant.venue_constraints.values_list('category_id', 'priority')), {(keep.pk, 3), (new.pk, 4)})
        self.assertEqual(old.venueconstraint_set.count(), 0)
        self.assertTrue(VenueCategory.objects.filter(pk=old.pk).exists())

    def test_venue_constraint_removal_validation(self):
        category = self.categories[0]
        foreign = VenueCategory.objects.create(tournament=Tournament.objects.create(slug='other'), name='Other')
        category_url = self.link('api-venuecategory-detail', category)
        foreign_url = reverse_tournament('api-venuecategory-detail', foreign.tournament, kwargs={'pk': foreign.pk})
        for participant, endpoint in self.venue_cases:
            participant.venue_constraints.create(category=category, priority=1)
            invalid = [[category_url], [category_url.rsplit('/', 1)[0] + '/999999999']]
            if isinstance(participant, Institution):
                response = self.client.patch(self.link(endpoint, participant), {'remove_venue_constraints': [foreign_url]})
                self.assertEqual(response.status_code, 200, response.data)
            else:
                invalid.append([foreign_url])
            for removal in invalid:
                response = self.client.patch(self.link(endpoint, participant), {
                    'venue_constraints': [{'category': category_url, 'priority': 2}], 'remove_venue_constraints': removal,
                })
                self.assertEqual(response.status_code, 400, response.data)
                self.assertEqual(list(participant.venue_constraints.values_list('priority', flat=True)), [1])

    def test_venue_constraint_removal_rolls_back(self):
        category, _, new = self.categories
        other = self.institutions[1].venue_constraints.create(category=category, priority=1)
        for participant, endpoint in self.venue_cases:
            participant.venue_constraints.create(category=category, priority=1)
            with patch.object(type(participant), 'save', side_effect=RuntimeError('save failed')), self.assertLogs('api.exceptions', level='ERROR'):
                response = self.client.patch(self.link(endpoint, participant), {
                    'venue_constraints': [{'category': self.link('api-venuecategory-detail', new), 'priority': 2}],
                    'remove_venue_constraints': [self.link('api-venuecategory-detail', category)],
                })
            self.assertEqual(response.status_code, 500)
            self.assertEqual(list(participant.venue_constraints.values_list('category_id', 'priority')), [(category.pk, 1)])
            response = self.client.patch(self.link(endpoint, participant), {'remove_venue_constraints': [self.link('api-venuecategory-detail', category)]})
            self.assertEqual(response.status_code, 200, response.data)
            self.assertTrue(type(other).objects.filter(pk=other.pk).exists())

    def test_venue_constraint_removal_permissions(self):
        context = {'request': APIRequestFactory().get('/'), 'tournament': self.tournament, 'view': None}
        context['request'].user = AnonymousUser()
        with patch('api.serializers.has_permission', return_value=False):
            for serializer in [TeamSerializer, AdjudicatorSerializer, PerTournamentInstitutionSerializer]:
                self.assertNotIn('remove_venue_constraints', serializer(context=context).fields)
