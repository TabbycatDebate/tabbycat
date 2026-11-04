from types import SimpleNamespace
from unittest.mock import patch

from api.fields import AnonymisingParticipantNameField, SideChoiceField
from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase
from rest_framework.serializers import Serializer

from participants.models import Adjudicator, Speaker
from users.permissions import Permission


class SideSerializer(Serializer):
    side = SideChoiceField()


class SideChoiceFieldTests(SimpleTestCase):

    def test_representation(self):
        cases = [
            (2, 'aff-neg', [(-1, 'bye'), (0, 'aff'), (1, 'neg'), (2, 2), (3, 3), (-2, -2)]),
            (4, 'bp', [(-1, 'bye'), (0, 'og'), (1, 'oo'), (2, 'cg'), (3, 'co'), (4, 4), (-2, -2)]),
            (2, '1-2', [(-1, -1), (0, 0), (1, 1), (2, 2)]),
            (3, 'aff-neg', [(-1, 'bye'), (0, 0), (2, 2)]),
        ]
        for team_count, side_names, values in cases:
            tournament = SimpleNamespace(pref={'teams_in_debate': team_count, 'side_names': side_names}.__getitem__)
            for value, expected in values:
                with self.subTest(team_count=team_count, side_names=side_names, value=value):
                    data = SideSerializer({'side': value}, context={'tournament': tournament}).data
                    self.assertEqual(data['side'], expected)


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
