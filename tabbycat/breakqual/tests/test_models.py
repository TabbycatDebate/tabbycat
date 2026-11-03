from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.test import TestCase

from breakqual.base import StandardBreakGenerator
from breakqual.models import BreakCategory, BreakingTeam
from breakqual.views import BreakCategoryModelForm
from participants.models import Team
from tournaments.models import Tournament


class BreakCategoryTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(name="Break category test", slug="break-category-test")

    def make_category(self, break_size):
        return BreakCategory(
            tournament=self.tournament,
            name="Category",
            slug="category",
            seq=1,
            break_size=break_size,
            is_general=False,
            priority=1,
        )

    def test_zero_size_is_valid_and_has_no_break_rounds(self):
        category = self.make_category(0)

        category.full_clean()

        self.assertEqual(category.num_break_rounds, 0)

    def test_sizes_between_zero_and_two_are_invalid(self):
        for break_size in (-1, 1):
            with self.subTest(break_size=break_size), self.assertRaises(ValidationError):
                self.make_category(break_size).full_clean()

    def test_zero_size_is_valid_in_four_team_category_form(self):
        self.tournament.preferences['debate_rules__teams_in_debate'] = 4
        form_class = modelform_factory(
            BreakCategory,
            form=BreakCategoryModelForm,
            fields=('name', 'tournament', 'slug', 'break_size', 'is_general', 'priority', 'limit'),
        )
        form = form_class(
            data={
                'name': 'Category',
                'tournament': self.tournament.id,
                'slug': 'category',
                'break_size': 0,
                'priority': 1,
                'limit': 0,
            },
            tournament=self.tournament,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_generating_zero_size_break_clears_existing_break(self):
        category = self.make_category(0)
        category.save()
        team = Team.objects.create(
            tournament=self.tournament,
            reference="Team",
            use_institution_prefix=False,
        )
        team.break_categories.add(category)
        BreakingTeam.objects.create(break_category=category, team=team, rank=1, break_rank=1)

        StandardBreakGenerator(category).generate()

        self.assertFalse(category.breakingteam_set.exists())
