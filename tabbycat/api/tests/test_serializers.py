from rest_framework.test import APIClient, APITestCase

from tournaments.models import Round
from utils.misc import reverse_round, reverse_tournament
from utils.tests import CompletedTournamentTestMixin


class RoundSerializerTests(CompletedTournamentTestMixin, APITestCase):

    # user = User.objects.get(username='admin')

    def test_exclude_motions_if_list(self):
        response = self.client.get(reverse_tournament('api-round-list', self.tournament))
        self.assertIsNone(response.data[0].get('motions'))

    def test_include_motions_if_released(self):
        round = self.tournament.round_set.first()
        round.motions_released = True
        round.save()

        response = self.client.get(reverse_round('api-round-detail', self.tournament.round_set.first()))
        self.assertEqual(len(response.data.get('motions')), 3)

    def test_exclude_feedback_weight_public(self):
        response = self.client.get(reverse_tournament('api-round-list', self.tournament))
        self.assertIsNone(response.data[0].get('feedback_weight'))

    def test_include_feedback_weight_admin(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse_tournament('api-round-list', self.tournament))
        self.assertIsNotNone(response.data[0].get('feedback_weight'))

    def test_seq_validation(self):
        client = APIClient()
        client.login(username="admin", password="admin")
        response = client.post(reverse_tournament('api-round-list', self.tournament), {
            'motions': [],
            'seq': 1,
            'name': 'Round 1',
            'abbreviation': 'R1',
            'draw_type': 'R',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['seq'][0], 'Object with same value exists in the tournament')

    def test_break_category_validation(self):
        client = APIClient()
        client.login(username="admin", password="admin")
        round = self.tournament.round_set.filter(stage=Round.Stage.ELIMINATION).first()
        response = client.patch(reverse_round('api-round-detail', round), {
            'break_category': None,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], 'Rounds are elimination iff they have a break category.')

    def test_can_create_round(self):
        client = APIClient()
        client.login(username="admin", password="admin")
        self.tournament.round_set.get(seq=5).delete()
        response = client.post(reverse_tournament('api-round-list', self.tournament), {
            'motions': [{
                'text': 'THW test code',
                'reference': 'Test',
                'seq': 1,
            }],
            'seq': 5,
            'name': 'Round 5',
            'abbreviation': 'R5',
            'draw_type': 'P',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['motions']), 1)

    def test_can_update_round_motion(self):
        client = APIClient()
        client.login(username="admin", password="admin")
        round = self.tournament.round_set.get(seq=5)
        round.roundmotion_set.all().delete()
        motion = round.prev.motion_set.first()
        response = client.patch(reverse_round('api-round-detail', round), {
            'motions': [
                {
                    'pk': motion.id,
                    'text': motion.text,
                    'reference': 'Test',
                },
                {
                    'text': 'THW write tests',
                    'reference': 'Unit Test',
                },
            ],
            'name': 'Round Five',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Round Five')


class MotionSerializerTests(CompletedTournamentTestMixin, APITestCase):

    def test_create_motion_with_round(self):
        client = APIClient()
        client.login(username="admin", password="admin")
        response = client.post(reverse_tournament('api-motion-list', self.tournament), {
            'text': 'This House would straighten all bananas',
            'reference': 'Bananas',
            'info_slide': 'Get bent',
            'rounds': [{'seq': 4, 'round': 'http://testserver/api/v1/tournaments/demo/rounds/1'}],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['rounds']), 1)


class AdjudicatorSerializerTests(CompletedTournamentTestMixin, APITestCase):

    def test_create_adj_null_institution(self):
        client = APIClient()
        client.login(username="admin", password="admin")
        response = client.post(reverse_tournament('api-adjudicator-list', self.tournament), {
            "name": "string",
            "gender": "M",
            "email": "user@example.com",
            "phone": "string",
            "anonymous": True,
            "pronoun": "string",
            "institution": None,
            "base_score": 0,
            "breaking": False,
            "trainee": False,
            "independent": True,
            "adj_core": False,
            "institution_conflicts": [],
            "team_conflicts": [],
            "adjudicator_conflicts": [],
            "url_key": "laZzBPo6FsGEr12VtB8LSHM8",
        })
        self.assertEqual(response.status_code, 201)
