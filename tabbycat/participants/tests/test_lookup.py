from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from participants.models import Institution, Region, Team
from tournaments.models import Tournament


class TestParticipantLookup(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="main")
        self.region = Region.objects.create()
        self.institution = Institution.objects.create(name="An Institution", code="Inst",
                region=self.region)

        # team1 uses institution prefix, team2 does not
        self.team1 = Team.objects.create(institution=self.institution, reference="The First",
                short_reference="1", use_institution_prefix=True, tournament=self.tournament)
        self.team2 = Team.objects.create(institution=self.institution, reference="The Second",
                short_reference="2", use_institution_prefix=False, tournament=self.tournament)

    def tearDown(self):
        self.team1.delete()
        self.team2.delete()
        self.institution.delete()
        self.region.delete()
        self.tournament.delete()

    def test_institution_lookup(self):
        self.assertEqual(Institution.objects.lookup("An Institution"), self.institution)
        self.assertEqual(Institution.objects.lookup("Inst"), self.institution)
        self.assertRaises(ObjectDoesNotExist, Institution.objects.lookup, "randomstring")

    def test_team_lookup(self):
        self.assertEqual(Team.objects.lookup("An Institution The First"), self.team1)
        self.assertEqual(Team.objects.lookup("Inst 1"), self.team1)
        self.assertEqual(Team.objects.lookup("The Second"), self.team2)
        self.assertEqual(Team.objects.lookup("2"), self.team2)
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "randomstring")

    def test_invalid_team_lookup(self):
        # These names are inconsistent with the use_institution_prefix setting, so should fail lookup
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "The First")
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "1")
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "An Institution The Second")
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "Inst 2")

    def test_institution_lookup_with_region(self):
        other_region = Region.objects.create()
        self.assertEqual(Institution.objects.lookup("An Institution", region=self.region), self.institution)
        self.assertEqual(Institution.objects.lookup("Inst", region=self.region), self.institution)
        self.assertRaises(ObjectDoesNotExist, Institution.objects.lookup, "An Institution", region=other_region)
        self.assertRaises(ObjectDoesNotExist, Institution.objects.lookup, "Inst", region=other_region)
        other_region.delete()

    def test_team_lookup_with_tournament(self):
        other_tournament = Tournament.objects.create(slug="other")
        self.assertEqual(Team.objects.lookup("An Institution The First", tournament=self.tournament), self.team1)
        self.assertEqual(Team.objects.lookup("Inst 1", tournament=self.tournament), self.team1)
        self.assertEqual(Team.objects.lookup("The Second", tournament=self.tournament), self.team2)
        self.assertEqual(Team.objects.lookup("2", tournament=self.tournament), self.team2)
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "An Institution The First", tournament=other_tournament)
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "Inst 1", tournament=other_tournament)
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "The Second", tournament=other_tournament)
        self.assertRaises(ObjectDoesNotExist, Team.objects.lookup, "2", tournament=other_tournament)
        other_tournament.delete()
