import logging

from django.utils.translation import gettext_lazy as _

from .preferences import tournament_preferences_registry

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


def public_presets_for_form():
    return [(_('Public Information Options'), _('Enable Public Information')),
            (False, _('Disable Public Information'))]


def get_preferences_data(selected_preset, tournament):
    preset_preferences = []
    # Create an instance of the class and iterate over its properties for the UI
    for key in dir(selected_preset):
        value = getattr(selected_preset, key)
        if '__' in key and not key.startswith('__'):
            # Lookup the base object
            section, name = key.split('__', 1)
            try:
                preset_object = tournament_preferences_registry[section][name]
                current_value = tournament.preferences[key]
            except KeyError:
                logger.exception("Bad preference key: %s", key)
                continue
            preset_preferences.append({
                'key': key,
                'name': preset_object.verbose_name,
                'current_value': current_value,
                'new_value': value,
                'help_text': preset_object.help_text,
                'changed': current_value != value,
            })
    preset_preferences.sort(key=lambda x: x['key'])
    return preset_preferences


class PreferencesPreset:
    show_in_list                               = False


class AustralsPreferences(PreferencesPreset):
    name         = _("Australs Rules")
    description  = _("3 vs 3 with replies, chosen motions, intermediate brackets, "
        "one-up-one-down. Compliant with AIDA rules.")
    show_in_list = True

    # Scoring
    scoring__score_min                         = 70.0 # Technically the speaks
    scoring__score_max                         = 80.0 # range is at the adj
    scoring__score_step                        = 1.0  # core's discretion (it's
    scoring__reply_score_min                   = 35.0 # not in the constitution)
    scoring__reply_score_max                   = 40.0
    scoring__reply_score_step                  = 0.5
    scoring__maximum_margin                    = 0.0  # Rob Confirmed
    # Draws
    draw_rules__avoid_same_institution         = True
    draw_rules__avoid_team_history             = True
    draw_rules__draw_odd_bracket               = 'intermediate_bubble_up_down'
    draw_rules__draw_side_allocations          = 'balance'
    draw_rules__draw_pairing_method            = 'slide'
    draw_rules__draw_avoid_conflicts           = 'one_up_one_down'
    # Debate Rules
    debate_rules__teams_in_debate              = 'two'
    debate_rules__ballots_per_debate_prelim    = 'per-adj'
    debate_rules__ballots_per_debate_elim      = 'per-adj'
    debate_rules__substantive_speakers         = 3
    debate_rules__reply_scores_enabled         = True
    debate_rules__motion_vetoes_enabled        = True
    debate_rules__side_names                   = 'aff-neg'
    data_entry__enable_motions                 = True
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

    scoring__score_min                         = 50.0
    scoring__score_max                         = 99.0
    scoring__score_step                        = 1.0
    scoring__maximum_margin                    = 0.0
    # Debate Rules
    debate_rules__substantive_speakers         = 2
    debate_rules__teams_in_debate              = 'bp'
    debate_rules__ballots_per_debate_prelim    = 'per-debate'
    debate_rules__ballots_per_debate_elim      = 'per-debate'
    debate_rules__speakers_in_ballots          = 'prelim'
    debate_rules__side_names                   = 'gov-opp'
    debate_rules__reply_scores_enabled         = False
    debate_rules__motion_vetoes_enabled        = False
    data_entry__enable_motions                 = False
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
    scoring__score_min                         = 50.0
    scoring__score_max                         = 100.0
    # Debate Rules
    debate_rules__reply_scores_enabled         = False # Not scored
    debate_rules__substantive_speakers         = 2
    debate_rules__side_names                   = 'gov-opp'
    debate_rules__motion_vetoes_enabled        = False
    debate_rules__ballots_per_debate_prelim    = 'per-debate'
    debate_rules__ballots_per_debate_elim      = 'per-debate'
    data_entry__enable_motions                 = False
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
    scoring__score_min                         = 70.0
    scoring__score_max                         = 80.0
    scoring__maximum_margin                    = 15.0
    # Debate Rules
    debate_rules__reply_scores_enabled         = False
    debate_rules__motion_vetoes_enabled        = True
    data_entry__enable_motions                 = True
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
    scoring__score_min                         = 60.0
    scoring__score_max                         = 80.0
    scoring__reply_score_min                   = 30.0
    scoring__reply_score_max                   = 40.0
    # Debate Rules
    debate_rules__reply_scores_enabled         = True
    debate_rules__motion_vetoes_enabled        = True
    data_entry__enable_motions                 = True
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
    scoring__score_min                         = 60.0
    scoring__score_max                         = 80.0
    scoring__reply_score_min                   = 30.0
    scoring__reply_score_max                   = 40.0
    # Debate Rules
    debate_rules__reply_scores_enabled         = True
    debate_rules__motion_vetoes_enabled        = False
    data_entry__enable_motions                 = False
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

    # Rules source = http://www.alcheringa.in/pdrules.pdf
    # Scoring
    scoring__score_min                         = 69.0  # From Rules Book
    scoring__score_max                         = 81.0  # From Rules Book
    scoring__score_step                        = 1.0
    scoring__reply_score_min                   = 34.5  # Not specified; assuming half of substantive
    scoring__reply_score_max                   = 42.0  # Not specified; assuming  half of substantive
    scoring__reply_score_step                  = 0.5
    scoring__maximum_margin                    = 0.0   # TODO= check this
    scoring__margin_includes_dissenters        = True  # From Rules:10.9.5
    # Draws
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = True
    draw_rules__draw_odd_bracket               = 'pullup_top'  # From Rules 10.3.1
    draw_rules__draw_side_allocations          = 'balance'  # From Rules 10.6
    draw_rules__draw_pairing_method            = 'slide'  # From rules 10.5
    draw_rules__draw_avoid_conflicts           = 'one_up_one_down'  # From rules 10.6.4
    # Debate Rules
    debate_rules__substantive_speakers         = 3
    debate_rules__reply_scores_enabled         = True
    debate_rules__motion_vetoes_enabled        = True
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
    scoring__score_min                         = 60.0
    scoring__score_max                         = 80.0
    scoring__score_step                        = 1.0
    scoring__reply_score_min                   = 30.0
    scoring__reply_score_max                   = 40.0
    scoring__reply_score_step                  = 0.5
    # Data
    data_entry__enable_motions                 = False # Single motions per round
    # Debates
    debate_rules__motion_vetoes_enabled        = False # Single motions per round
    debate_rules__side_names                   = 'prop-opp'
    # Draws (exact mechanism is up to the host)
    draw_rules__avoid_same_institution         = False
    # Standings
    standings__team_standings_precedence       = ['wins', 'num_adjs', 'speaks_avg']
    standings__speaker_standings_precedence    = ['average']  # speakers sub in/out
    # UI Options
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = False


class WADLPreferences(PreferencesPreset):
    name         = "WADL Options"
    show_in_list = False
    description  = ("Example high school setup. Many features not "
        "supported in conjunction with other settings.")

    # Debate Rules= no replies; singular motions
    debate_rules__substantive_speakers         = 3
    debate_rules__reply_scores_enabled         = False
    debate_rules__motion_vetoes_enabled        = False
    data_entry__enable_motions                 = False
    # Standings Rules
    standings__standings_missed_debates        = 0
    standings__team_standings_precedence       = ['points', 'wbw', 'margin_avg', 'speaks_avg']
    standings__speaker_standings_precedence    = ['average']
    standings__speaker_standings_extra_metrics = ['stdev', 'count']
    # Draws
    draw_rules__avoid_same_institution         = False
    draw_rules__avoid_team_history             = False
    draw_rules__draw_odd_bracket               = 'intermediate_bubble_up_down'
    draw_rules__draw_side_allocations          = 'balance'
    draw_rules__draw_pairing_method            = 'slide'
    draw_rules__draw_avoid_conflicts           = 'one_up_one_down'
    # UI Options
    ui_options__show_emoji                     = False
    ui_options__show_team_institutions         = False
    ui_options__show_adjudicator_institutions  = False
    ui_options__show_speakers_in_draw          = False
    ui_options__public_motions_order           = 'reverse'
    public_features__public_draw               = 'all-released'
    public_features__public_results            = True
    public_features__public_motions            = True
    public_features__public_record             = False


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
