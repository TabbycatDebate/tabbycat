from registration.forms import AdminSpeakerForm, SpeakerForm, TeamForm
from utils.tests import BaseMinimalTournamentTestCase


class RegistrationCategoryFieldsTestCase(BaseMinimalTournamentTestCase):

    def setUp(self):
        super().setUp()
        self.tournament._prefs['reg_team_fields'] = ['break_categories']
        self.tournament._prefs['reg_speaker_fields'] = ['categories']
        self.team = self.tournament.team_set.first()

    def create_break_category(self, name, is_general, seq):
        return self.tournament.breakcategory_set.create(
            name=name, slug=name.lower(), seq=seq, break_size=4,
            is_general=is_general, priority=seq)

    def test_team_hides_break_categories_without_eligible_choices(self):
        self.assertNotIn('break_categories', TeamForm(self.tournament).fields)
        self.create_break_category("Open", is_general=True, seq=1)
        self.assertNotIn('break_categories', TeamForm(self.tournament).fields)

    def test_team_renders_only_eligible_break_category_checkboxes(self):
        self.create_break_category("Open", is_general=True, seq=1)
        category = self.create_break_category("Novice", is_general=False, seq=2)
        form = TeamForm(self.tournament)
        html = str(form['break_categories'])
        self.assertIn('type="checkbox"', html)
        self.assertIn(f'value="{category.pk}"', html)
        self.assertIn('Novice', html)
        self.assertNotIn('Open', html)
        self.assertEqual(html.count('type="checkbox"'), 1)

    def test_speaker_hides_categories_without_public_choices(self):
        self.assertNotIn('categories', SpeakerForm(self.team, None).fields)
        self.tournament.speakercategory_set.create(name="Private", slug='private', seq=1, public=False)
        self.assertNotIn('categories', SpeakerForm(self.team, None).fields)

    def test_speaker_renders_only_public_category_checkboxes(self):
        self.tournament.speakercategory_set.create(name="Private", slug='private', seq=1, public=False)
        category = self.tournament.speakercategory_set.create(name="Novice", slug='novice', seq=2, public=True)
        form = SpeakerForm(self.team, None)
        html = str(form['categories'])
        self.assertIn('type="checkbox"', html)
        self.assertIn(f'value="{category.pk}"', html)
        self.assertIn('Novice', html)
        self.assertNotIn('Private', html)
        self.assertEqual(html.count('type="checkbox"'), 1)

    def test_preferences_can_hide_populated_category_fields(self):
        self.create_break_category("Novice", is_general=False, seq=1)
        self.tournament.speakercategory_set.create(name="Novice", slug='novice', seq=1, public=True)
        self.tournament._prefs['reg_team_fields'] = []
        self.tournament._prefs['reg_speaker_fields'] = []
        self.assertNotIn('break_categories', TeamForm(self.tournament).fields)
        self.assertNotIn('categories', SpeakerForm(self.team, None).fields)


class AdminSpeakerFormTestCase(BaseMinimalTournamentTestCase):

    def setUp(self):
        super().setUp()
        self.team = self.tournament.team_set.first()
        self.category = self.tournament.speakercategory_set.create(
            name="Novice", slug="novice", seq=1, public=False)

    def test_shows_all_fields_regardless_of_preferences(self):
        form = AdminSpeakerForm(team=self.team)
        for name in ('name', 'last_name', 'email', 'phone', 'gender', 'categories'):
            self.assertIn(name, form.fields)
        self.assertNotIn('key', form.fields)

    def test_all_fields_optional_except_name(self):
        form = AdminSpeakerForm(team=self.team)
        self.assertTrue(form.fields['name'].required)
        for name in ('last_name', 'email', 'phone', 'gender', 'categories'):
            self.assertFalse(form.fields[name].required, name)

    def test_includes_non_public_categories(self):
        form = AdminSpeakerForm(team=self.team)
        self.assertIn(self.category, form.fields['categories'].queryset)

    def test_save_with_name_only(self):
        form = AdminSpeakerForm(team=self.team, data={'name': "Jane Doe"})
        self.assertTrue(form.is_valid(), form.errors)
        speaker = form.save()
        self.assertEqual(speaker.team, self.team)
        self.assertTrue(speaker.url_key)

    def test_registration_form_still_filters_fields(self):
        form = SpeakerForm(self.team, None)
        self.assertNotIn('last_name', form.fields)
        if 'categories' in form.fields:
            self.assertNotIn(self.category, form.fields['categories'].queryset)

    def test_save_with_name_only_without_categories(self):
        self.tournament.speakercategory_set.all().delete()
        form = AdminSpeakerForm(team=self.team, data={'name': "Jane Doe"})
        self.assertNotIn('categories', form.fields)
        self.assertTrue(form.is_valid(), form.errors)
        speaker = form.save()
        self.assertEqual(speaker.name, "Jane Doe")
        self.assertEqual(speaker.team, self.team)
        self.assertFalse(speaker.categories.exists())
