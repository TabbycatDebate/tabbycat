from registration.forms import AdminSpeakerForm, SpeakerForm
from utils.tests import BaseMinimalTournamentTestCase


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
