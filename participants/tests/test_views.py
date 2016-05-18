import json

from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from participants.models import Speaker, Adjudicator
from tournaments.models import Tournament

client = Client()

class PublicParticipantsViewTestCase(TestCase):

    fixtures = ['completed_demo.json',]

    def setUp(self):
        self.t = Tournament.objects.first()

    def test_unset_preference(self):
        self.t.preferences['public_features__public_participants'] = False

        response = self.client.get(reverse('public_participants',
           kwargs={'tournament_slug': self.t.slug}))

        # 302 redirect shoould be issued if setting is not enabled
        self.assertEqual(response.status_code, 302)

    def test_set_preference(self):
        self.t.preferences['public_features__public_participants'] = True

        response = self.client.get(reverse('public_participants',
           kwargs={'tournament_slug': self.t.slug}))

        # 200 OK should be issued if setting is not enabled
        self.assertEqual(response.status_code, 200)

        # Check number of adjs matches
        adj_models = Adjudicator.objects.filter(tournament=self.t).count()
        adj_json = len(json.loads(response.context['tableDataA']))
        self.assertEqual(adj_models, adj_json)

        # Check number of speakers matches
        speaker_models = Speaker.objects.filter(team__tournament=self.t).count()
        speakers_json = len(json.loads(response.context['tableDataB']))
        self.assertEqual(speaker_models, speakers_json)

