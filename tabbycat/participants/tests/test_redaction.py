from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import SimpleTestCase

from participants.models import Adjudicator, Speaker
from participants.tables import TeamResultTableBuilder


class RecordRedactionTests(SimpleTestCase):

    def setUp(self):
        self.preferences = {'teams_in_debate': 2, 'participant_code_names': 'off', 'team_code_names': 'off'}
        self.tournament = SimpleNamespace(slug='test', pref=self.preferences.__getitem__)
        self.speaker = Speaker(pk=1, name='Private Speaker', code_name='Speaker Alias', anonymous=True)

    def test_score_tooltips(self):
        cases = [
            (False, False, True, 'off', '<em>Redacted</em>'),
            (False, True, True, 'off', '<em>Redacted</em>'),
            (True, False, True, 'off', '<em>Redacted</em>'),
            (True, True, True, 'off', 'Private Speaker'),
            (False, False, False, 'everywhere', 'Speaker Alias'),
            (False, False, False, 'off', 'Private Speaker'),
        ]
        for admin, permitted, anonymous, code_names, expected in cases:
            with self.subTest(admin=admin, permitted=permitted, anonymous=anonymous, code_names=code_names):
                self.speaker.anonymous = anonymous
                self.preferences['participant_code_names'] = code_names
                table = TeamResultTableBuilder(tournament=self.tournament, admin=admin)
                scores = [SimpleNamespace(debate_team=SimpleNamespace(speaker_scores=[
                    SimpleNamespace(score=75, speaker=self.speaker),
                ]))]
                with patch('participants.tables.has_permission', return_value=permitted):
                    table.add_speaker_scores_column(scores)
                self.assertEqual(table.data[0][0]['text'], '75')
                self.assertEqual(table.data[0][0]['tooltip'], '75 for ' + expected)

    def test_record_cards_redact_names_in_admin_sections(self):
        adjudicator = Adjudicator(name='Private Judge', anonymous=True)
        speaker = SimpleNamespace(pk=1, name=self.speaker.name, get_public_name=self.speaker.get_public_name)
        judge = SimpleNamespace(name=adjudicator.name, get_public_name=adjudicator.get_public_name)
        context = Context({
            'tournament': self.tournament,
            'user': AnonymousUser(),
            'admin_page': True,
            'pref': {'team_code_names': 'off', 'show_speakers_in_draw': True},
            'team': SimpleNamespace(pk=1, short_name='Team', speakers=[speaker]),
            'adjudicator': judge,
        })
        for template_name, private_name in [
            ('team_registration_card.html', self.speaker.name),
            ('adjudicator_registration_card.html', adjudicator.name),
        ]:
            with self.subTest(template=template_name):
                with patch('utils.templatetags.debate_tags.has_permission', return_value=True):
                    rendered = Template('{% include "' + template_name + '" %}').render(context)
                self.assertNotIn(private_name, rendered)
                self.assertIn('<summary><em>Redacted</em></summary>', rendered)
                if template_name == 'team_registration_card.html':
                    self.assertIn('flex-grow-1"><em>Redacted</em></span>', rendered)
