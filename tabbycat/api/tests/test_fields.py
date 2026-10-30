from types import SimpleNamespace
from unittest.mock import patch

from api.fields import AnonymisingParticipantNameField, TournamentHyperlinkedRelatedField
from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase
from rest_framework.serializers import Serializer

from participants.models import Adjudicator, Speaker
from tournaments.models import Tournament
from users.permissions import Permission


class TournamentHyperlinkedRelatedFieldTests(SimpleTestCase):

    def test_adjudicator_url_tournament(self):
        class AdjudicatorLinkSerializer(Serializer):
            adjudicator = TournamentHyperlinkedRelatedField(view_name='api-adjudicator-detail', read_only=True)

        tournament = Tournament(slug='own-tournament')
        context_tournament = Tournament(slug='context-tournament')
        for object_tournament, context, expected_slug in (
            (None, {'tournament': context_tournament}, 'context-tournament'),
            (tournament, {'tournament': context_tournament}, 'own-tournament'),
            (tournament, {}, 'own-tournament'),
        ):
            with self.subTest(object_tournament=object_tournament, context=context):
                adjudicator = Adjudicator(pk=42, tournament=object_tournament)
                data = AdjudicatorLinkSerializer(
                    SimpleNamespace(adjudicator=adjudicator), context={'request': None, **context},
                ).data
                self.assertEqual(data['adjudicator'], f'/api/v1/tournaments/{expected_slug}/adjudicators/42')


class ParticipantNameSerializer(Serializer):
    name = AnonymisingParticipantNameField()


class ParticipantNameRedactionTests(SimpleTestCase):

    def test_names_require_permission_to_unredact(self):
        cases = [
            (True, 'off', set(), None),
            (True, 'off', {Permission.VIEW_PARTICIPANT_DECODED}, None),
            (True, 'off', {Permission.VIEW_ANONYMOUS}, 'Private Name'),
            (False, 'off', set(), 'Private Name'),
            (False, 'everywhere', set(), 'Public Alias'),
            (False, 'everywhere', {Permission.VIEW_PARTICIPANT_DECODED}, 'Private Name'),
        ]
        for model in (Speaker, Adjudicator):
            for anonymous, code_names, permissions, expected in cases:
                with self.subTest(model=model.__name__, anonymous=anonymous, code_names=code_names, permissions=permissions):
                    participant = model(name='Private Name', code_name='Public Alias', anonymous=anonymous)
                    context = {
                        'view': object(),
                        'request': SimpleNamespace(user=SimpleNamespace(is_anonymous=False)),
                        'tournament': SimpleNamespace(pref=lambda key: code_names),
                    }
                    with patch('api.fields.has_permission', side_effect=lambda user, permission, tournament: permission in permissions):
                        data = ParticipantNameSerializer(participant, context=context).data
                    self.assertEqual(data['name'], expected)

    def test_public_request_redacts_anonymous_name(self):
        participant = Speaker(name='Private Name', anonymous=True)
        context = {
            'view': object(),
            'request': SimpleNamespace(user=AnonymousUser()),
            'tournament': SimpleNamespace(),
        }
        self.assertIsNone(ParticipantNameSerializer(participant, context=context).data['name'])

    def test_schema_context_preserves_name(self):
        participant = Speaker(name='Private Name', anonymous=True)
        self.assertEqual(ParticipantNameSerializer(participant).data['name'], 'Private Name')
