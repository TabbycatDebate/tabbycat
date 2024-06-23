import logging
from copy import copy
from decimal import Decimal

from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .forms import tournament_preference_form_builder

logger = logging.getLogger(__name__)


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

    @classmethod
    def get_preferences(cls):
        for key in dir(cls):
            if '__' in key and not key.startswith('__'):
                yield key

    @classmethod
    def get_form(cls, tournament, **kwargs):
        form = tournament_preference_form_builder(tournament, [tuple(key.split('__', 1)[::-1]) for key in cls.get_preferences()])(**kwargs)
        for field in form:
            # Copying required to avoid blanks added to list fields
            field.initial = copy(getattr(cls, field.name))
            field.changed = tournament.preferences[field.name] != getattr(cls, field.name)
        return form

    @classmethod
    def save(cls, tournament):
        for pref in cls.get_preferences():
            logger.info(f"Setting {pref} to {getattr(cls, pref)}")
            tournament.preferences[pref] = getattr(cls, pref)


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

    scoring__score_min                         = Decimal('50')
    scoring__score_max                         = Decimal('99')
    scoring__score_step                        = Decimal('1')
    scoring__maximum_margin                    = 0.0
    scoring__teamscore_includes_ghosts         = True  # WUDC 34.9.3.2
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
    # Standings Rules
    standings__standings_missed_debates        = -1 # Speakers always show
    standings__team_standings_precedence       = ['points', 'speaks_sum', 'firsts', 'seconds']
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

    # Rules source = https://docs.google.com/document/d/10AVKBhev_OFRtorWsu2VB9B5V1a2f20425HYkC5ztMM/edit
    # Scoring
    scoring__score_min                         = Decimal('69')  # From Rules Book
    scoring__score_max                         = Decimal('81')  # From Rules Book
    scoring__score_step                        = Decimal('1')
    scoring__reply_score_min                   = Decimal('34.5')  # Not specified; assuming half of substantive
    scoring__reply_score_max                   = Decimal('42.0')  # Not specified; assuming half of substantive
    scoring__reply_score_step                  = Decimal('0.5')
    scoring__maximum_margin                    = 0.0   # TODO= check this
    scoring__margin_includes_dissenters        = False  # From Rules 20.3.2
    # Draws
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = True
    draw_rules__draw_odd_bracket               = 'pullup_top'  # From Rules 20.10
    draw_rules__draw_pullup_restriction        = 'least_to_date'  # From Rules 20.11
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

    # Rules source = http://mkf2v40tlr04cjqkt2dtlqbr.wpengine.netdna-cdn.com/wp-content/uploads/2014/05/WSDC-Debate-Rules-U-2015.pdf
    # Score (strictly specified in the rules)
    scoring__score_min                         = Decimal('60')
    scoring__score_max                         = Decimal('80')
    scoring__score_step                        = Decimal('1')
    scoring__reply_score_min                   = Decimal('30.0')
    scoring__reply_score_max                   = Decimal('40.0')
    scoring__reply_score_step                  = Decimal('0.5')
    # Debates
    motions__motion_vetoes_enabled             = False # Single motions per round
    motions__enable_motions                    = False
    debate_rules__side_names                   = 'prop-opp'
    # Draws (exact mechanism is up to the host)
    draw_rules__avoid_same_institution         = False
    # Standings
    standings__team_standings_precedence       = ['wins', 'num_adjs', 'speaks_avg']
    standings__speaker_standings_precedence    = ['average']  # speakers sub in/out
    # UI Options
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = False


class APDAPreferences(PreferencesPreset):
    name = _("APDA Rules")
    show_in_list = True
    description = _("2 vs 2 with speech rankings and byes")

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


class PublicSpeaking(PreferencesPreset):
    name = _("Public Speaking")
    show_in_list = True
    description = _("Arbitrary number of teams per room, one speech each, no team points")

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
