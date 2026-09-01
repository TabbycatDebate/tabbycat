from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from options.fields import EMPTY_CHOICE
from options.presets import APDAPreferences, get_preset_from_slug, PreferencesPreset, WSDCPreferences
from results.models import ScoreCriterion
from tournaments.models import Round, Tournament


class TestPreset(PreferencesPreset):
    name         = "Test Rules"
    description  = "Used for unit tests"
    show_in_list = False

    # Scoring
    scoring__score_min = Decimal('70')
    scoring__score_max = Decimal('80')


class TestPresets(TestCase):
    def set_up_tournament(self):
        tournament = Tournament.objects.create(slug="preset", name="Preset Testing")
        tournament.preferences['scoring__score_min'] = Decimal('0')
        tournament.preferences['scoring__score_max'] = Decimal('100')
        return tournament

    @patch('options.presets.all_presets', return_value=[TestPreset])
    def test_get_preset_good_slug(self, mock_all_presets):
        self.assertEqual(get_preset_from_slug('testpreset'), TestPreset)

    @patch('options.presets.all_presets', return_value=[])
    def test_get_preset_slug_invalid(self, mock_all_presets):
        with self.assertRaises(ValueError):
            get_preset_from_slug('testpreset')

    @patch('options.presets.all_presets', return_value=[TestPreset, TestPreset])
    def test_get_preset_many_presets(self, mock_all_presets):
        with self.assertLogs('options.presets', level='WARNING') as cm:
            self.assertEqual(get_preset_from_slug('testpreset'), TestPreset)
            self.assertEqual(cm.output, ['WARNING:options.presets:Found more than one preset for testpreset'])

    def test_preferences_does_not_include_meta(self):
        self.assertFalse('name' in list(TestPreset.get_preferences()))

    def test_preferences_includes_all_preferences(self):
        self.assertTrue(set(TestPreset.get_preferences()) == {'scoring__score_min', 'scoring__score_max'})

    def test_can_save_preset(self):
        tournament = self.set_up_tournament()
        TestPreset.save(tournament)

        for pref, new_val in [('scoring__score_min', Decimal('70')), ('scoring__score_max', Decimal('80'))]:
            self.assertEqual(tournament.preferences[pref], new_val)

        tournament.delete()

    def test_can_create_form(self):
        tournament = self.set_up_tournament()

        form = TestPreset.get_form(tournament)
        self.assertEqual(form.preset_action_rows, ())

        for pref, new_val in [('scoring__score_min', Decimal('70')), ('scoring__score_max', Decimal('80'))]:
            self.assertTrue(pref in form.fields)
            self.assertEqual(form[pref].initial, new_val)
            self.assertEqual(form[pref].changed, True)

        tournament.delete()

    def test_can_save_preset_form(self):
        tournament = self.set_up_tournament()

        form = TestPreset.get_form(tournament, data={'scoring__score_min': Decimal('70'), 'scoring__score_max': Decimal('80')})
        form.is_valid()
        form.update_preferences()

        for pref, new_val in [('scoring__score_min', Decimal('70')), ('scoring__score_max', Decimal('80'))]:
            self.assertEqual(tournament.preferences[pref], new_val)

        tournament.delete()

    def test_apda_preset_form_includes_apply_action_checkbox(self):
        tournament = self.set_up_tournament()
        form = APDAPreferences.get_form(tournament)
        self.assertTrue(hasattr(form, 'preset_action_rows'))
        self.assertEqual(len(form.preset_action_rows), 1)
        action, field = form.preset_action_rows[0]
        self.assertEqual(action.id, 'seed_first_prelim_draw')
        self.assertIn('preset_action__seed_first_prelim_draw', form.fields)
        self.assertIn('scoring__score_min', form.fields)
        tournament.delete()

    def test_apda_preset_action_split_when_first_prelim_already_seeded(self):
        tournament = self.set_up_tournament()
        Round.objects.create(
            tournament=tournament,
            seq=1,
            name='Round 1',
            abbreviation='R1',
            stage=Round.Stage.PRELIMINARY,
            draw_type=Round.DrawType.SEEDED,
        )
        form = APDAPreferences.get_form(tournament)
        self.assertEqual(len(form.preset_action_rows_pending), 0)
        self.assertEqual(len(form.preset_action_rows_already), 1)
        self.assertEqual(form.preset_action_rows_already[0][0].id, 'seed_first_prelim_draw')
        tournament.delete()

    def _apda_form_data(self, **extra):
        precedence = APDAPreferences.standings__speaker_standings_precedence
        base = {
            'scoring__score_min': APDAPreferences.scoring__score_min,
            'scoring__score_max': APDAPreferences.scoring__score_max,
            'motions__motion_vetoes_enabled': APDAPreferences.motions__motion_vetoes_enabled,
            'motions__enable_motions': APDAPreferences.motions__enable_motions,
            'draw_rules__draw_odd_bracket': APDAPreferences.draw_rules__draw_odd_bracket,
            'draw_rules__team_institution_penalty': APDAPreferences.draw_rules__team_institution_penalty,
            'draw_rules__team_history_penalty': APDAPreferences.draw_rules__team_history_penalty,
            'draw_rules__draw_pairing_method': APDAPreferences.draw_rules__draw_pairing_method,
            'draw_rules__draw_pullup_restriction': APDAPreferences.draw_rules__draw_pullup_restriction,
            'draw_rules__bye_team_results': APDAPreferences.draw_rules__bye_team_results,
            'draw_rules__bye_team_selection': APDAPreferences.draw_rules__bye_team_selection,
            'draw_rules__draw_avoid_conflicts': APDAPreferences.draw_rules__draw_avoid_conflicts,
            'draw_rules__pullup_debates_penalty': APDAPreferences.draw_rules__pullup_debates_penalty,
            'draw_rules__side_penalty': APDAPreferences.draw_rules__side_penalty,
            'draw_rules__pairing_penalty': APDAPreferences.draw_rules__pairing_penalty,
            'debate_rules__ballots_per_debate_prelim': APDAPreferences.debate_rules__ballots_per_debate_prelim,
            'debate_rules__ballots_per_debate_elim': APDAPreferences.debate_rules__ballots_per_debate_elim,
            'debate_rules__winners_in_ballots': APDAPreferences.debate_rules__winners_in_ballots,
            'debate_rules__speakers_in_ballots': APDAPreferences.debate_rules__speakers_in_ballots,
            'debate_rules__substantive_speakers': APDAPreferences.debate_rules__substantive_speakers,
            'debate_rules__side_names': APDAPreferences.debate_rules__side_names,
            'debate_rules__reply_scores_enabled': APDAPreferences.debate_rules__reply_scores_enabled,
            'debate_rules__speaker_ranks': APDAPreferences.debate_rules__speaker_ranks,
        }
        for i in range(4):
            key = 'standings__speaker_standings_precedence_%d' % i
            base[key] = precedence[i] if i < len(precedence) else EMPTY_CHOICE
        base.update(extra)
        return base

    def test_apda_apply_action_sets_first_prelim_round_seeded(self):
        tournament = self.set_up_tournament()
        Round.objects.create(
            tournament=tournament,
            seq=1,
            name='Round 1',
            abbreviation='R1',
            stage=Round.Stage.PRELIMINARY,
            draw_type=Round.DrawType.RANDOM,
        )
        form = APDAPreferences.get_form(
            tournament,
            data=self._apda_form_data(preset_action__seed_first_prelim_draw='on'),
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.update_preferences()
        first = tournament.round_set.get(seq=1)
        self.assertEqual(first.draw_type, Round.DrawType.SEEDED)
        tournament.delete()

    def test_apda_apply_action_skipped_when_checkbox_off(self):
        tournament = self.set_up_tournament()
        Round.objects.create(
            tournament=tournament,
            seq=1,
            name='Round 1',
            abbreviation='R1',
            stage=Round.Stage.PRELIMINARY,
            draw_type=Round.DrawType.RANDOM,
        )
        form = APDAPreferences.get_form(tournament, data=self._apda_form_data())
        self.assertTrue(form.is_valid(), form.errors)
        form.update_preferences()
        first = tournament.round_set.get(seq=1)
        self.assertEqual(first.draw_type, Round.DrawType.RANDOM)
        tournament.delete()

    def test_apda_save_runs_default_enabled_apply_actions(self):
        tournament = self.set_up_tournament()
        Round.objects.create(
            tournament=tournament,
            seq=1,
            name='Round 1',
            abbreviation='R1',
            stage=Round.Stage.PRELIMINARY,
            draw_type=Round.DrawType.RANDOM,
        )
        APDAPreferences.save(tournament)
        first = tournament.round_set.get(seq=1)
        self.assertEqual(first.draw_type, Round.DrawType.SEEDED)
        tournament.delete()

    def test_wsdc_save_creates_score_criteria(self):
        tournament = self.set_up_tournament()

        WSDCPreferences.save(tournament)

        criteria = list(tournament.scorecriterion_set.order_by('seq'))
        self.assertEqual(
            [(c.name, c.speech_type, c.min_score, c.max_score, c.step, c.required) for c in criteria],
            [
                ('Style', ScoreCriterion.SpeechType.SUBSTANTIVE, 24, 32, 0.5, True),
                ('Content', ScoreCriterion.SpeechType.SUBSTANTIVE, 24, 32, 0.5, True),
                ('Strategy', ScoreCriterion.SpeechType.SUBSTANTIVE, 12, 16, 0.5, True),
                ('POIs', ScoreCriterion.SpeechType.SUBSTANTIVE, -2, 2, 0.5, False),
                ('Style', ScoreCriterion.SpeechType.REPLY, 12, 16, 0.5, True),
                ('Content', ScoreCriterion.SpeechType.REPLY, 12, 16, 0.5, True),
                ('Strategy', ScoreCriterion.SpeechType.REPLY, 6, 8, 0.5, True),
            ],
        )
        tournament.delete()

    def test_wsdc_score_criteria_action_is_idempotent(self):
        tournament = self.set_up_tournament()
        WSDCPreferences.save(tournament)
        criterion_ids = list(tournament.scorecriterion_set.order_by('seq').values_list('id', flat=True))

        WSDCPreferences.save(tournament)

        self.assertEqual(
            list(tournament.scorecriterion_set.order_by('seq').values_list('id', flat=True)),
            criterion_ids,
        )
        self.assertFalse(WSDCPreferences._wsdc_score_criteria_would_change(tournament))
        tournament.delete()
