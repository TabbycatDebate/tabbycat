import json

from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from tournaments.models import Tournament

class PublicResultsForRoundViewTestCase(TestCase):

    fixtures = ['completed_demo.json']

    def setUp(self):
        self.t = Tournament.objects.first()

    def test_unset_preference(self):
        self.t.preferences['public_features__public_results'] = False

        response = self.client.get(reverse('public_results',
           kwargs={'round_seq': 3}))

        # 302 redirect shoould be issued if setting is not enabled
        self.assertEqual(response.status_code, 302)

    def test_set_preference(self):
        self.t.preferences['public_features__public_results'] = True

        response = self.client.get(reverse('public_participants',
           kwargs={'tournament_slug': 3}))

        # 200 OK should be issued if setting is not enabled
        self.assertEqual(response.status_code, 200)