from django.conf import settings
from django.urls import reverse
from dynamic_preferences.registries import global_preferences_registry
from rest_framework.test import APITestCase

from utils.tests import CompletedTournamentTestMixin


class RootTests(APITestCase):

    def test_get_root(self):
        response = self.client.get(reverse('api-root'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "_links": {"v1": "http://testserver/api/v1"},
            "timezone": settings.TIME_ZONE,
            "version": settings.TABBYCAT_VERSION,
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
                "tournaments": "http://testserver/api/v1/tournaments",
                "institutions": "http://testserver/api/v1/institutions",
                "users": "http://testserver/api/v1/users",
            },
        })


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
