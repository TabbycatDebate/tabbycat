import logging
from copy import copy
from decimal import Decimal
from typing import Any, Callable, NamedTuple

from django import forms
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .forms import tournament_preference_form_builder, TournamentPreferenceForm

logger = logging.getLogger(__name__)


class PresetApplyAction(NamedTuple):
    """Labelled side effect run when a preset is applied (not stored as a preference)."""

    id: str
    label: Any
    apply: Callable[[Any], None]
    default_enabled: bool = True
    would_change: Callable[[Any], bool] | None = None

    def is_changed_for_tournament(self, tournament: Any) -> bool:
        if self.would_change is not None:
            return self.would_change(tournament)
        return True


def _all_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from _all_subclasses(subclass)
        yield subclass


def all_presets():
    yield from _all_subclasses(PreferencesPreset)


def presets_for_form():
    presets = all_presets()
    choices = []
    for index, preset in enumerate(presets):
        if preset.show_in_list:
            choices.append((preset.name, preset.name))

    choices.sort(key=lambda x: x[1]) # Sort by name
    return choices


public_presets_for_form = [
    (True, _('Enable Public Information')),
    (False, _('Disable Public Information')),
]


data_entry_presets_for_form = [
    (False, _('Disabled (tab staff only)')),
    ("private-urls", _('Use private URLs')),
    ("public", _('Use publicly accessible form')),
]


def get_preset_from_slug(slug):
    selected_presets = [x for x in all_presets() if slugify(x.__name__) == slug]
    if len(selected_presets) == 0:
        raise ValueError("Preset {!r} not found.".format(slug))
    elif len(selected_presets) > 1:
        logger.warning("Found more than one preset for %s", slug)
    return selected_presets[0]


class PreferencesPreset:
    show_in_list                               = False
    apply_actions                              = ()

    @classmethod
    def get_preferences(cls):
        for key in dir(cls):
            if '__' in key and not key.startswith('__'):
                yield key

    @classmethod
    def get_apply_actions(cls):
        return cls.apply_actions

    @classmethod
    def _run_apply_actions(cls, tournament, selected_action_ids):
        """selected_action_ids None: run each action where default_enabled (CLI / configure).
        Otherwise run only ids present in the set (preset form checkboxes)."""
        for action in cls.get_apply_actions():
            if selected_action_ids is None:
                if not action.default_enabled:
                    continue
            elif action.id not in selected_action_ids:
                continue
            logger.info("Applying preset action %s for tournament %s", action.id, tournament.slug)
            action.apply(tournament)

    @classmethod
    def get_form(cls, tournament, **kwargs):
        pref_tuples = [tuple(key.split('__', 1)[::-1]) for key in cls.get_preferences()]
        BaseForm = tournament_preference_form_builder(tournament, pref_tuples)  # noqa: N806
        action_specs = list(cls.get_apply_actions())
        if action_specs:

            def update_preferences(self, **kwargs):
                # Not a normal class-body method: zero-arg super() is invalid here.
                TournamentPreferenceForm.update_preferences(self, **kwargs)
                inst = self.manager.instance
                selected = {a.id for a in action_specs if self.cleaned_data.get(f'preset_action__{a.id}')}
                cls._run_apply_actions(inst, selected)

            attrs = {
                'update_preferences': update_preferences,
            }
            for a in action_specs:
                attrs[f'preset_action__{a.id}'] = forms.BooleanField(
                    label=a.label,
                    required=False,
                    initial=a.default_enabled,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                )
            FormClass = type('PresetFormWithApplyActions', (BaseForm,), attrs)  # noqa: N806
            form = FormClass(**kwargs)
            form.preset_action_rows = tuple((a, form[f'preset_action__{a.id}']) for a in action_specs)
        else:
            form = BaseForm(**kwargs)
            form.preset_action_rows = ()

        actions_by_id = {a.id: a for a in action_specs}
        for field in form:
            if field.name.startswith('preset_action__'):
                aid = field.name[len('preset_action__'):]
                spec = actions_by_id.get(aid)
                field.changed = spec.is_changed_for_tournament(tournament) if spec else True
                continue
            # Copying required to avoid blanks added to list fields
            field.initial = copy(getattr(cls, field.name))
            field.changed = tournament.preferences[field.name] != getattr(cls, field.name)

        if action_specs:
            pending_rows, already_rows = [], []
            for a in action_specs:
                bf = form[f'preset_action__{a.id}']
                if bf.changed:
                    pending_rows.append((a, bf))
                else:
                    already_rows.append((a, bf))
            form.preset_action_rows_pending = tuple(pending_rows)
            form.preset_action_rows_already = tuple(already_rows)
        else:
            form.preset_action_rows_pending = ()
            form.preset_action_rows_already = ()

        return form

    @classmethod
    def save(cls, tournament):
        for pref in cls.get_preferences():
            logger.info(f"Setting {pref} to {getattr(cls, pref)}")
            tournament.preferences[pref] = getattr(cls, pref)
        cls._run_apply_actions(tournament, None)


class AustralsPreferences(PreferencesPreset):
    name         = _("Australs Rules")
    description  = _("3 vs 3 with replies, chosen motions, intermediate brackets, "
        "one-up-one-down. Compliant with AIDA rules.")
    show_in_list = True

    # Scoring
    scoring__score_min                         = Decimal('70') # Technically the speaks
    scoring__score_max                         = Decimal('80') # range is at the adj
    scoring__score_step                        = Decimal('1')  # core's discretion (it's
    scoring__reply_score_min                   = Decimal('35.0') # not in the constitution)
    scoring__reply_score_max                   = Decimal('40.0')
    scoring__reply_score_step                  = Decimal('0.5')
    scoring__maximum_margin                    = 0.0  # Rob Confirmed
    # Draws
    draw_rules__avoid_same_institution         = True
    draw_rules__avoid_team_history             = True
    draw_rules__draw_odd_bracket               = 'intermediate_bubble_up_down'
    draw_rules__draw_side_allocations          = 'balance'
    draw_rules__draw_pairing_method            = 'slide'
    draw_rules__draw_avoid_conflicts           = 'one_up_one_down'
    # Debate Rules
    debate_rules__teams_in_debate              = 2
    debate_rules__ballots_per_debate_prelim    = 'per-adj'
    debate_rules__ballots_per_debate_elim      = 'per-adj'
    debate_rules__substantive_speakers         = 3
    debate_rules__reply_scores_enabled         = True
    debate_rules__side_names                   = 'aff-neg'
    motions__motion_vetoes_enabled             = True
    motions__enable_motions                    = True
    # Standings Rules
    standings__standings_missed_debates        = 2  # TODO= check this
    standings__team_standings_precedence       = ['wins', 'speaks_sum']
    standings__speaker_standings_precedence    = ['average'] # constitutional
    standings__speaker_standings_extra_metrics = ['stdev', 'count']
    # UI Options
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = True


class BritishParliamentaryPreferences(PreferencesPreset):
    name         = _("British Parliamentary Rules")
    description  = _("2 vs 2 vs 2 vs 2. Compliant with WUDC rules.")
    show_in_list = True

    # WUDC Constitution: https://docs.google.com/document/d/19Hk8imODwOIr6zLCUUwqpAhSamoSqmL0ZdoeemY_XD0/edit?tab=t.0
    scoring__score_min                         = Decimal('50')
    scoring__score_max                         = Decimal('100') # WUDC Schedule 1: 5.3
    scoring__score_step                        = Decimal('1')
    scoring__maximum_margin                    = 0.0
    scoring__teamscore_includes_ghosts         = True  # WUDC 35.9.3.2
    # Debate Rules
    debate_rules__substantive_speakers         = 2
    debate_rules__teams_in_debate              = 4
    debate_rules__ballots_per_debate_prelim    = 'per-debate'
    debate_rules__ballots_per_debate_elim      = 'per-debate'
    debate_rules__speakers_in_ballots          = 'prelim'
    debate_rules__side_names                   = 'gov-opp'
    debate_rules__reply_scores_enabled         = False
    debate_rules__preparation_time             = 15
    motions__motion_vetoes_enabled             = False
    motions__enable_motions                    = False
    # Draw Rules
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = False
    draw_rules__bp_pullup_distribution         = 'anywhere'
    draw_rules__bp_position_cost               = 'entropy'
    draw_rules__bp_renyi_order                 = 1.0
    draw_rules__bp_position_cost_exponent      = 4.0
    draw_rules__bp_assignment_method           = 'hungarian_preshuffled'
    draw_rules__draw_pullup_penalty            = 100000
    # Standings Rules
    standings__standings_missed_debates        = -1 # Speakers always show
    standings__team_standings_precedence       = ['points', 'speaks_sum', 'firsts', 'seconds', 'draw_strength']
    standings__speaker_standings_precedence    = ['total'] # constitutional
    standings__speaker_standings_extra_metrics = ['average', 'stdev']
    # Feedback Rules
    feedback__adj_max_score                    = 10.0
    # UI Options
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = True
    # Email Sending - replace "wins" by "points"
    team_points_email_subject                  = "{{ TEAM }}'s current points after {{ ROUND }}: {{ POINTS }}"
    team_points_email_message                  = ("<p>Hi {{ USER }},</p>",
        "<p>Your team ({{ TEAM }}) currently has <strong>{{ POINTS }}</strong> points in the {{ TOURN }}.",
        "<p>Current Standings: {{ URL }}</p>")


class CanadianParliamentaryPreferences(PreferencesPreset):
    name         = _("Canadian Parliamentary Rules")
    show_in_list = True
    description  = _("2 vs 2 with replies (unscored) and POIs. May require "
        "additional configuration depending on regional variations.")
    # Scoring
    scoring__score_min                         = Decimal('50')
    scoring__score_max                         = Decimal('100')
    # Debate Rules
    debate_rules__reply_scores_enabled         = False # Not scored
    debate_rules__substantive_speakers         = 2
    debate_rules__side_names                   = 'gov-opp'
    debate_rules__ballots_per_debate_prelim    = 'per-debate'
    debate_rules__ballots_per_debate_elim      = 'per-debate'
    motions__motion_vetoes_enabled             = False
    motions__enable_motions                    = False
    # Draws
    draw_rules__avoid_same_institution         = False # TBC
    draw_rules__avoid_team_history             = False # TBC
    draw_rules__draw_odd_bracket               = 'pullup_top' # TBC
    draw_rules__draw_side_allocations          = 'balance'
    draw_rules__draw_pairing_method            = 'fold' # TBC
    draw_rules__draw_avoid_conflicts           = 'off'


class AustralianEastersPreferences(AustralsPreferences):
    name         = _("Australian Easters Rules")
    show_in_list = True
    description  = _("3 vs 3 without replies, set motions, novices, intermediate "
        "bubbles, one-up-one-down. Compliant with AIDA rules.")

    # Scoring
    scoring__score_min                         = Decimal('70')
    scoring__score_max                         = Decimal('80')
    scoring__maximum_margin                    = 15.0
    # Debate Rules
    debate_rules__reply_scores_enabled         = False
    motions__motion_vetoes_enabled             = True
    motions__enable_motions                    = True
    debate_rules__ballots_per_debate_prelim    = 'per-debate'
    debate_rules__ballots_per_debate_elim      = 'per-adj'
    # Standings Rules
    standings__speaker_standings_precedence    = ['average']  # constitutional


class NZEastersPreferences(AustralsPreferences):
    name         = _("2 vs 2 Impromptu")
    show_in_list = True
    description  = _("2 vs 2 with replies, chosen motions, chosen sides, and "
        "novice statuses.")

    # Scoring
    scoring__score_min                         = Decimal('60')
    scoring__score_max                         = Decimal('80')
    scoring__reply_score_min                   = Decimal('30.0')
    scoring__reply_score_max                   = Decimal('40.0')
    # Debate Rules
    debate_rules__reply_scores_enabled         = True
    motions__motion_vetoes_enabled             = True
    motions__enable_motions                    = True
    debate_rules__substantive_speakers         = 2
    # Standings
    standings__team_standings_precedence       = ['wins', 'wbw', 'speaks_sum', 'wbw', 'draw_strength', 'wbw']
    # Draw Rules
    draw_rules__draw_side_allocations          = 'manual-ballot'
    draw_rules__draw_odd_bracket               = 'intermediate'
    draw_rules__draw_pairing_method            = 'fold'
    draw_rules__draw_avoid_conflicts           = 'off'
    draw_rules__avoid_same_institution         = False # TODO: CHECK
    draw_rules__avoid_team_history             = False # TODO: CHECK


class JoyntPreferences(AustralsPreferences):
    name         = _("3 vs 3 Prepared")
    show_in_list = True
    description  = _("3 vs 3 with preallocated sides, publicly displayed sides "
        "and motions, and novice statuses.")

    # Scoring
    scoring__score_min                         = Decimal('60')
    scoring__score_max                         = Decimal('80')
    scoring__reply_score_min                   = Decimal('30.0')
    scoring__reply_score_max                   = Decimal('40.0')
    # Debate Rules
    debate_rules__reply_scores_enabled         = True
    motions__motion_vetoes_enabled             = False
    motions__enable_motions                    = False
    debate_rules__substantive_speakers         = 3
    # Draw Rules
    draw_rules__draw_side_allocations          = 'preallocated'
    draw_rules__draw_odd_bracket               = 'intermediate2'
    draw_rules__draw_pairing_method            = 'fold'
    draw_rules__draw_avoid_conflicts           = 'off'
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = False
    # Standings
    standings__team_standings_precedence       = ['wins', 'wbw', 'speaks_sum', 'wbw', 'draw_strength', 'wbw']
    # Public Features
    public_features__public_side_allocations   = True


class UADCPreferences(AustralsPreferences):
    name         = _("UADC Rules")
    show_in_list = True
    description  = _("3 vs 3 with replies, chosen motions, and all adjudicators "
        "can receive feedback from teams.")

    # Rules source = https://docs.google.com/document/d/1yoRcSR3mufyzOTxbOTxnGvdfxS-ODscVPN3CzzoD3mQ/edit?tab=t.0#heading=h.scv1sbq5r6yj
    # Handbook source = https://docs.google.com/document/d/1JoJa0oqDfW06vAQb3eBcAX37oG9p2g0hRO44vvCHv_Q/edit?tab=t.0
    # Scoring
    scoring__score_min                         = Decimal('67')  # From Handbook 2.8.2
    scoring__score_max                         = Decimal('83')  # From Handbook 2.8.2
    scoring__score_step                        = Decimal('1')
    scoring__reply_score_min                   = Decimal('33.5')  # From Handbook 2.8.2
    scoring__reply_score_max                   = Decimal('41.5')  # From Handbook 2.8.2
    scoring__reply_score_step                  = Decimal('0.5')
    scoring__maximum_margin                    = 0.0   # TODO= check this
    scoring__margin_includes_dissenters        = False  # From Rules 20.3.2
    # Draws
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = True
    draw_rules__draw_odd_bracket               = 'intermediate_bubble_up_down'  # From Rules 20.6
    draw_rules__draw_side_allocations          = 'balance'
    draw_rules__draw_pairing_method            = 'slide'  # From rules 20.9
    draw_rules__draw_avoid_conflicts           = 'one_up_one_down'  # From rules 10.6.4
    # Debate Rules
    debate_rules__substantive_speakers         = 3
    debate_rules__reply_scores_enabled         = True
    motions__motion_vetoes_enabled             = True
    debate_rules__side_names                   = 'gov-opp'
    # Standings Rules
    standings__team_standings_precedence       = ['wins', 'speaks_sum', 'margin_avg']
    # Feedback
    feedback__adj_min_score                    = 1.0   # Explicit in the rules
    feedback__adj_max_score                    = 10.0  # Explicit in the rules
    feedback__feedback_from_teams              = 'all-adjs' # Kinda a big deal
    # UI Options
    public_features__feedback_progress         = True  # Feedback is compulsory


class WSDCPreferences(AustralsPreferences):
    name         = _("WSDC Rules")
    show_in_list = True
    description  = _("3 vs 3 with replies, chosen motions, prop/opp side labels, "
        "and all adjudicators can receive feedback from teams.")

    score_criteria = (
        ('Style', 'S', Decimal('24'), Decimal('32'), True),
        ('Content', 'S', Decimal('24'), Decimal('32'), True),
        ('Strategy', 'S', Decimal('12'), Decimal('16'), True),
        ('POIs', 'S', Decimal('-2'), Decimal('2'), False),
        ('Style', 'R', Decimal('12'), Decimal('16'), True),
        ('Content', 'R', Decimal('12'), Decimal('16'), True),
        ('Strategy', 'R', Decimal('6'), Decimal('8'), True),
    )

    @staticmethod
    def _wsdc_score_criteria_match(tournament):
        actual = list(tournament.scorecriterion_set.order_by('seq').values_list(
            'seq', 'name', 'speech_type', 'weight', 'min_score', 'max_score', 'step', 'required',
        ))
        expected = [
            (seq, name, speech_type, 1.0, min_score, max_score, 0.5, required)
            for seq, (name, speech_type, min_score, max_score, required)
            in enumerate(WSDCPreferences.score_criteria, start=1)
        ]
        return actual == expected

    @staticmethod
    def _apply_wsdc_score_criteria(tournament):
        if WSDCPreferences._wsdc_score_criteria_match(tournament):
            return

        from django.db import transaction
        from results.models import ScoreCriterion

        with transaction.atomic():
            tournament.scorecriterion_set.all().delete()
            ScoreCriterion.objects.bulk_create([
                ScoreCriterion(
                    tournament=tournament,
                    name=name,
                    seq=seq,
                    speech_type=speech_type,
                    weight=1,
                    min_score=min_score,
                    max_score=max_score,
                    step=0.5,
                    required=required,
                )
                for seq, (name, speech_type, min_score, max_score, required)
                in enumerate(WSDCPreferences.score_criteria, start=1)
            ])

    @staticmethod
    def _wsdc_score_criteria_would_change(tournament):
        return not WSDCPreferences._wsdc_score_criteria_match(tournament)

    apply_actions = (
        PresetApplyAction(
            id='wsdc_score_criteria',
            label=_('Replace score criteria with the WSDC criteria'),
            apply=_apply_wsdc_score_criteria,
            default_enabled=True,
            would_change=_wsdc_score_criteria_would_change,
        ),
    )

    # Rules source = https://www.wsdcdebating.org/_files/ugd/669183_399cb065fe31455b9371bd8dfdf7e0d1.pdf
    # Score (strictly specified in the rules)
    scoring__score_min                         = Decimal('60')
    scoring__score_max                         = Decimal('80')
    scoring__score_step                        = Decimal('0.5')
    scoring__reply_score_min                   = Decimal('30.0')
    scoring__reply_score_max                   = Decimal('40.0')
    scoring__reply_score_step                  = Decimal('0.5')
    scoring__margin_includes_dissenters        = True # Important
    # Debates
    motions__motion_vetoes_enabled             = False # Single motions per round
    motions__enable_motions                    = False
    debate_rules__side_names                   = 'prop-opp'
    # Draws (exact mechanism is up to the host)
    # Draw source = https://www.wsdcdebating.org/_files/ugd/669183_acd9f3bd3ab3482ebead22ae0da74fa7.pdf
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = True # Rule 3.9
    draw_rules__draw_pairing_method            = 'fold' # Rule 3.8
    draw_rules__draw_odd_bracket               = 'pullup_top' # Rule 3.7
    draw_rules__max_times_per_side             = 5
    # Tabbycat currently does not support WSDC-style pull up and so not fully support WSDC-style draw creation.
    # Hence, this below setting is the closest that we can manage to achive.
    # TODO: Update when Tabbycat can support WSDC pull-up.
    draw_rules__draw_side_allocations          = 'balance'
    draw_rules__draw_avoid_conflicts           = 'graph_one'
    draw_rules__draw_pullup_restriction        = 'lowest_ds_wins'
    # Standings
    standings__team_standings_precedence       = ['wins', 'num_adjs', 'speaks_avg'] # Rule 3.2 (2023 version)
    standings__speaker_standings_precedence    = ['average']  # speakers sub in/out
    # UI Options
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = False


class APDAPreferences(PreferencesPreset):
    name = _("APDA Rules")
    show_in_list = True
    description = _("2 vs 2 with speech rankings and byes")

    @staticmethod
    def _apda_apply_seed_first_prelim_draw(tournament):
        Round = tournament.round_set.model  # noqa: N806
        first = tournament.round_set.filter(stage=Round.Stage.PRELIMINARY).order_by('seq').first()
        if first is None:
            return
        first.draw_type = Round.DrawType.SEEDED
        first.save(update_fields=['draw_type'])

    @staticmethod
    def _apda_seed_first_prelim_would_change(tournament):
        Round = tournament.round_set.model  # noqa: N806
        first = tournament.round_set.filter(stage=Round.Stage.PRELIMINARY).order_by('seq').first()
        return first is not None and first.draw_type != Round.DrawType.SEEDED

    apply_actions = (
        PresetApplyAction(
            id='seed_first_prelim_draw',
            label=_('Set round 1 preliminary draw type to Seeded'),
            apply=_apda_apply_seed_first_prelim_draw,
            default_enabled=True,
            would_change=_apda_seed_first_prelim_would_change,
        ),
    )

    scoring__score_min                         = Decimal('15')
    scoring__score_max                         = Decimal('40')
    motions__motion_vetoes_enabled             = False # Single motions per round
    motions__enable_motions                    = False
    draw_rules__draw_odd_bracket               = 'pullup_bottom'
    draw_rules__team_institution_penalty       = 1000
    draw_rules__team_history_penalty           = 100000
    draw_rules__draw_pairing_method            = 'fold'
    draw_rules__draw_pullup_restriction        = 'least_to_date'
    draw_rules__bye_team_results               = 'points'
    draw_rules__bye_team_selection             = 'lowest'
    draw_rules__draw_avoid_conflicts           = 'graph'
    draw_rules__pullup_debates_penalty         = 10000
    draw_rules__side_penalty                   = 100
    draw_rules__pairing_penalty                = 1
    debate_rules__ballots_per_debate_prelim    = 'per-debate'
    debate_rules__ballots_per_debate_elim      = 'per-debate'
    debate_rules__winners_in_ballots           = 'tied-points'
    debate_rules__speakers_in_ballots          = 'prelim'
    debate_rules__substantive_speakers         = 2
    debate_rules__side_names                   = 'gov-opp'
    debate_rules__reply_scores_enabled         = False
    debate_rules__speaker_ranks                = 'any'
    standings__speaker_standings_precedence    = ['average', 'srank', 'trimmed_mean']
    ui_options__show_seed_in_importer          = 'title'


class RoundRobinTwoTeam(PreferencesPreset):
    name = _("Round-robin (two-team)")
    show_in_list = False
    description = _("Two teams per room, preliminary rounds use round-robin (no random first round). "
        "Conflict-avoidance options are less relevant because pairings are fixed by schedule.")

    debate_rules__teams_in_debate = 2
    draw_rules__avoid_team_history = False
    draw_rules__avoid_same_institution = False
    ui_options__show_seed_in_importer = 'numeric'


class RoundRobinBP(PreferencesPreset):
    name = _("Round-robin (British Parliamentary)")
    show_in_list = False
    description = _("BP with preset balanced round-robin tables for 16 or 28 teams. "
        "Assign every team a unique seed from 1 to n before drawing.")

    debate_rules__teams_in_debate = 4
    draw_rules__avoid_team_history = False
    draw_rules__avoid_same_institution = False
    ui_options__show_seed_in_importer = 'numeric'


class PublicSpeaking(PreferencesPreset):
    name = _("Public Speaking")
    show_in_list = True
    description = _("Arbitrary number of teams per room, one speech each, no team points")

    @staticmethod
    def apply_all_draws_random(tournament):
        Round = tournament.round_set.model  # noqa: N806
        return tournament.round_set.filter(stage=Round.Stage.PRELIMINARY).update(draw_type=Round.DrawType.RANDOM)

    @staticmethod
    def are_some_draws_not_random(tournament):
        Round = tournament.round_set.model  # noqa: N806
        return tournament.round_set.filter(stage=Round.Stage.PRELIMINARY).exclude(draw_type=Round.DrawType.RANDOM).exists()

    apply_actions = (
        PresetApplyAction(
            id='all_draws_random',
            label=_('Set all preliminary draws to random (no power-pairing)'),
            apply=apply_all_draws_random,
            default_enabled=True,
            would_change=are_some_draws_not_random,
        ),
    )

    scoring__score_min                         = Decimal('50')
    scoring__score_max                         = Decimal('99')
    scoring__score_step                        = Decimal('1')
    scoring__maximum_margin                    = 0.0
    scoring__margin_includes_dissenters        = True  # Disables win/rank calculations
    # Debate Rules
    debate_rules__substantive_speakers         = 1
    debate_rules__teams_in_debate              = 6
    debate_rules__ballots_per_debate_prelim    = 'per-adj'
    debate_rules__ballots_per_debate_elim      = 'per-adj'
    debate_rules__speakers_in_ballots          = 'prelim'
    debate_rules__side_names                   = '1-2'
    debate_rules__reply_scores_enabled         = False
    motions__motion_vetoes_enabled             = False
    motions__enable_motions                    = False
    # Draw Rules
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = False
    # Standings
    standings__team_standings_precedence       = ['speaks_avg']


class PublicInformation(PreferencesPreset):
    name         = _("Public Information Options")
    show_in_list = False
    description  = _("For tournaments hosted online: this sets it up so that "
        "people can access the draw and other generally useful information "
        "via the tab site.")

    public_features__public_draw               = 'current'
    public_features__public_break_categories   = True
    public_features__public_results            = True
    public_features__public_motions            = True
    public_features__public_team_standings     = True


class TabRelease(PreferencesPreset):
    name         = _("Tab Release Options")
    show_in_list = False
    description  = _("For when a tab is ready to be released. This will publicly "
        "display the results of all rounds, the team tab, the speaker tab, etc")

    tab_release__team_tab_released             = True
    tab_release__speaker_tab_released          = True
    tab_release__motion_tab_released           = True
    tab_release__ballots_released              = True
    tab_release__all_results_released          = True
    public_features__public_diversity          = True
    public_features__public_results            = True
    public_features__public_breaking_teams     = True
    public_features__public_breaking_adjs      = True
    # Disable
    public_features__public_checkins           = False
    public_features__public_team_standings     = False
    public_features__public_draw               = 'off'
    public_features__public_break_categories   = False


class PrivateURLs(PreferencesPreset):
    name = _("Use Private URLs")
    show_in_list = False
    description = _("Enables participant data entry through private URLs.")

    data_entry__participant_ballots            = 'private-urls'
    data_entry__participant_feedback           = 'private-urls'


class PublicForms(PreferencesPreset):
    name = _("Use Public Forms")
    show_in_list = False
    description = _("Enables participant data entry through public forms.")

    data_entry__participant_ballots            = 'public'
    data_entry__participant_feedback           = 'public'
