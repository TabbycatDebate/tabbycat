from django.test import TestCase

from breakqual.models import BreakCategory, BreakingTeam
from participants.models import Institution, Person, Region, Speaker, Team
from tournaments.models import Tournament

from ..diversity import get_diversity_data_sets


class DiversityDataTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(name="Diversity test", slug="diversity-test")
        self.region = Region.objects.create(name="Region")
        self.institution = Institution.objects.create(name="Institution", code="Inst", region=self.region)
        self.team = Team.objects.create(
            tournament=self.tournament,
            institution=self.institution,
            reference="A",
            use_institution_prefix=False,
        )
        Speaker.objects.create(team=self.team, name="Speaker", gender=Person.GENDER_MALE)

    def test_breaking_speaker_in_multiple_categories_is_counted_once(self):
        for seq in range(2):
            category = BreakCategory.objects.create(
                tournament=self.tournament,
                name=f"Category {seq}",
                slug=f"category-{seq}",
                seq=seq,
                break_size=2,
                is_general=seq == 0,
                priority=seq,
            )
            BreakingTeam.objects.create(break_category=category, team=self.team, rank=1, break_rank=1)

        data = get_diversity_data_sets(self.tournament, for_public=False)

        breaking_gender = next(item for item in data['speakers_gender'] if item['title'] == "Breaking")
        breaking_region = next(item for item in data['speakers_region'] if item['title'] == "Breaking")
        self.assertEqual(sum(item['count'] for item in breaking_gender['data']), 1)
        self.assertEqual(sum(item['count'] for item in breaking_region['data']), 1)

    def test_region_chart_labels_use_region_ids(self):
        data = get_diversity_data_sets(self.tournament, for_public=False)

        all_speakers = next(item for item in data['speakers_region'] if item['title'] == "All Speakers")
        self.assertEqual(all_speakers['data'], [{'count': 1, 'label': self.region.id}])
