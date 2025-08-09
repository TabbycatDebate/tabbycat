import json

from django.conf import settings
from django.test import Client
from django.urls import reverse
from dynamic_preferences.registries import global_preferences_registry
from rest_framework.test import APITestCase

from utils.tests import CompletedTournamentTestMixin, V1_ROOT_URL


class RootTests(APITestCase):

    def test_get_root(self):
        response = self.client.get(reverse('api-root'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "_links": {"v1": V1_ROOT_URL},
            "timezone": settings.TIME_ZONE,
            "version": settings.TABBYCAT_VERSION,
            "version_name": settings.TABBYCAT_CODENAME,
        })

    def test_api_disabled_root(self):
        global_preferences_registry.manager()['global__enable_api'] = False
        response = self.client.get(reverse('api-root'))
        self.assertEqual(response.status_code, 401)

        # Re-enable API as tearDown
        global_preferences_registry.manager()['global__enable_api'] = True

    def test_get_v1_root(self):
        response = self.client.get(reverse('api-v1-root'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "_links": {
                "tournaments": V1_ROOT_URL + "/tournaments",
                "institutions": V1_ROOT_URL + "/institutions",
                "users": V1_ROOT_URL + "/users",
            },
        })


class TournamentViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def test_get_tournament_list(self):
        response = self.client.get(reverse('api-tournament-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_tournament_detail(self):
        response = self.client.get(self.reverse_url('api-tournament-detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.tournament.id)


class MotionViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def test_no_public_access_preferences(self):
        self.tournament.preferences['public_features__public_motions'] = False
        self.tournament.preferences['tab_release__motion_tab_released'] = False
        response = self.client.get(reverse('api-motion-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(response.status_code, 401)

    def test_exclude_unreleased_public(self):
        self.tournament.round_set.filter(seq=1).update(motions_released=True)

        self.tournament.preferences['public_features__public_motions'] = True
        self.tournament.preferences['tab_release__motion_tab_released'] = False
        response = self.client.get(reverse('api-motion-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        for motion in response.data:
            self.assertEqual(len(motion['rounds']), 1)
        self.tournament.round_set.filter(seq=1).update(motions_released=False) # Reset

    def test_include_unreleased_tab_public(self):
        self.tournament.preferences['public_features__public_motions'] = False
        self.tournament.preferences['tab_release__motion_tab_released'] = True
        response = self.client.get(reverse('api-motion-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 18)  # 6 rounds * 3 motions/round

    def test_unauthorized_motion_detail(self):
        self.tournament.preferences['public_features__public_motions'] = True
        self.tournament.preferences['tab_release__motion_tab_released'] = False
        # Motion with id exists
        response = self.client.get(reverse('api-motion-detail', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(response.status_code, 404)


class RoundViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        self.round_seq = 1
        super().setUp()

    def test_get_round_list(self):
        self.round_seq = None  # Unset since it isn't used for list
        response = self.client.get(self.reverse_url('api-round-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

    def test_get_round_detail(self):
        response = self.client.get(self.reverse_url('api-round-detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.round.id)

    def test_patch_round_detail(self):
        # Ensure the test will be valid first
        self.assertEqual(self.round.motions_released, False)

        self.client.login(username="admin", password="admin")

        response = self.client.patch(
            self.reverse_url('api-round-detail'),
            json.dumps({"motions_released": True}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['motions_released'], True)
        self.round.refresh_from_db()
        self.assertEqual(self.round.motions_released, True)

    def test_post_round_detail(self):
        # Ensure the test will be valid first
        self.assertEqual(self.round.silent, False)

        self.client.login(username="admin", password="admin")

        response = self.client.post(
            self.reverse_url('api-round-detail'),
            json.dumps({
                "break_category": None,
                "starts_at": None,
                "seq": 1,
                "completed": True,
                "name": "Round 1",
                "abbreviation": "R1",
                "stage": "P",
                "draw_type": "R",
                "draw_status": "R",
                "silent": True,
                "motions_released": False,
                "weight": 1,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['silent'], True)
        self.round.refresh_from_db()
        self.assertEqual(self.round.silent, True)


class SpeakerCategoryViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.tournament.speakercategory_set.create(name='sc1', slug='sc1', seq=1, public=False)
        self.tournament.speakercategory_set.create(name='sc2', slug='sc2', seq=2, public=True)

    def test_private_excluded_public(self):
        response = self.client.get(reverse('api-speakercategory-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(len(response.data), 1)

    def test_all_categories_authenticated(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-speakercategory-list', kwargs={'tournament_slug': self.tournament.slug}))
        self.assertEqual(len(response.data), 2)


class BreakEligibilityViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def test_get_eligible_teams(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-breakcategory-eligibility', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(len(response.data), 2)


class SpeakerEligibilityViewsetTests(CompletedTournamentTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.sc = self.tournament.speakercategory_set.create(name='sc1', slug='sc1', seq=1, public=False)
        self.sc.speaker_set.set(self.tournament.team_set.first().speaker_set.all())

    def test_get_eligible_speakers(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-speakercategory-eligibility', kwargs={'tournament_slug': self.tournament.slug, 'pk': self.sc.pk}))
        self.assertEqual(len(response.data), 2)

    def test_unauthorized_if_private(self):
        response = self.client.get(reverse('api-speakercategory-eligibility', kwargs={'tournament_slug': self.tournament.slug, 'pk': self.sc.pk}))
        self.assertEqual(response.status_code, 401)


class BreakingTeamsViewsetTests(CompletedTournamentTestMixin, APITestCase):
    client_class = Client

    def test_get_breaking_teams(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-breakcategory-break', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(len(response.data), 8)

    def test_generate_break(self):
        self.client.login(username="admin", password="admin")
        response = self.client.post(reverse('api-breakcategory-break', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(len(response.data), 13)

    def test_delete_break(self):
        self.client.login(username="admin", password="admin")
        response = self.client.delete(reverse('api-breakcategory-break', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}))
        self.assertEqual(response.status_code, 204)

    def test_remove_breaking_team(self):
        self.client.login(username="admin", password="admin")
        response = self.client.patch(reverse('api-breakcategory-break', kwargs={'tournament_slug': self.tournament.slug, 'pk': 1}), {
            'team': 'http://testserver/api/v1/tournaments/demo/teams/7',
            'remark': 'w',
        }, content_type='application/json')
        self.assertEqual(len(response.data), 16)


class BallotViewSetTests(CompletedTournamentTestMixin, APITestCase):

    def test_access_with_user_auth(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('api-ballot-list', kwargs={'tournament_slug': self.tournament.slug, 'round_seq': 1, 'debate_pk': 12}))
        self.assertEqual(response.status_code, 200)

    def test_access_with_private_url(self):
        response = self.client.get(reverse('api-ballot-list', kwargs={'tournament_slug': self.tournament.slug, 'round_seq': 1, 'debate_pk': 12}), headers={"Authorization": "Key urlkey"})
        self.assertEqual(response.status_code, 200)
