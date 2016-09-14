from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from participants.models import Adjudicator, Institution
from venues.models import Venue
from tournaments.models import Tournament


class TestSharing(TestCase):
    """Tests the sharing of venues and adjudicators, as returned by the
    `relevant_adjudicators` and `relevant_venues` properties of Tournament."""

    NUM_ATTACHED_ADJUDICATORS = 7
    NUM_ATTACHED_VENUES = 9
    NUM_FREE_ADJUDICATORS = 10
    NUM_FREE_VENUES = 13

    def setUp(self):
        self.tournament = Tournament.objects.create()
        for i in range(max(self.NUM_ATTACHED_ADJUDICATORS, self.NUM_FREE_ADJUDICATORS) // 2):
            Institution.objects.create(name=str(i))
        for i in range(self.NUM_ATTACHED_ADJUDICATORS):
            Adjudicator.objects.create(tournament=self.tournament, name=str(i),
                institution=Institution.objects.get(name=str(i // 2)))
        for i in range(self.NUM_ATTACHED_VENUES):
            Venue.objects.create(tournament=self.tournament, name=str(i), priority=i)
        for i in range(self.NUM_FREE_ADJUDICATORS):
            Adjudicator.objects.create(name=str(i),
                institution=Institution.objects.get(name=str(i // 2)))
        for i in range(self.NUM_FREE_VENUES):
            Venue.objects.create(name=str(i), priority=i)

    def tearDown(self):
        self.tournament.delete()
        Venue.objects.all().delete()
        Adjudicator.objects.all().delete()

    def test_venues_unshared(self):
        self.tournament.preferences['league_options__share_venues'] = False
        self.assertEqual(self.NUM_ATTACHED_VENUES, self.tournament.relevant_venues.count())
        for venue in self.tournament.relevant_venues.all():
            self.assertIsNotNone(venue.tournament)

    def test_venues_shared(self):
        self.tournament.preferences['league_options__share_venues'] = True
        self.assertEqual(self.NUM_ATTACHED_VENUES + self.NUM_FREE_VENUES,
                self.tournament.relevant_venues.count())

    def test_adjudicators_unshared(self):
        self.tournament.preferences['league_options__share_adjs'] = False
        self.assertEqual(self.NUM_ATTACHED_ADJUDICATORS, self.tournament.relevant_adjudicators.count())
        for adj in self.tournament.relevant_adjudicators.all():
            self.assertIsNotNone(adj.tournament)

    def test_adjudicators_shared(self):
        self.tournament.preferences['league_options__share_adjs'] = True
        self.assertEqual(self.NUM_ATTACHED_ADJUDICATORS + self.NUM_FREE_ADJUDICATORS,
                self.tournament.relevant_adjudicators.count())
