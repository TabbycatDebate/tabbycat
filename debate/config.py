from collections import OrderedDict
from django.forms import Select

def _bool(value):
    try:
        # 'True' and 'False' strings are stored in the database.
        # '0' and '1' is how it used to be stored, kept for backwards compatibility.
        # True and False (literals) are the default values.
        return {'True': True, 'False': False, '0': False, '1': True, True: True, False: False}[value]
    except KeyError:
        raise TypeError

#name,  coerce, help, default
SETTINGS = OrderedDict([
    ('substantive_speakers',        (int,   'How many substantive speakers each team will feature',                3)),
    ('score_min',                   (float, 'Minimum allowed score',                                               68)),
    ('score_max',                   (float, 'Maximum allowed score',                                               82)),
    ('score_step',                  (float, 'Score steps allowed',                                                 1)),
    ('reply_scores_enabled',        (_bool, 'Whether this style features reply speeches',                          True)),
    ('reply_score_min',             (float, 'Minimum allowed reply score',                                         34)),
    ('reply_score_max',             (float, 'Maximum allowed reply score',                                         41)),
    ('reply_score_step',            (float, 'Reply score steps allowed',                                           0.5)),
    ('maximum_margin',              (float, 'The largest amount one team can beat another by (0 means no limit)',  0.0)),
    ('break_size',                  (int,   'Number of breaking teams',                                            16)),
    ('esl_break_size',              (int,   'Number of ESL breaking teams',                                        8)),
    ('institution_cap',             (int,   'Maximum number of teams from one institution that can break. Set to 0 if there is no cap',         3)),
    ('motion_vetoes_enabled',       (_bool, 'Whether teams can veto motions',                                      True)),
    ('adj_min_score',               (float, 'Minimum adjudicator score',                                           1.5)),
    ('adj_max_score',               (float, 'Maximum adjudicator score',                                           5)),
    ('adj_chair_min_score',         (float, 'Minimum chair score',                                                 3.5)),
    ('draw_odd_bracket',            (str,   'Odd bracket resolution method, see wiki for allowed values',          'intermediate_bubble_up_down')),
    ('draw_side_allocations',       (str,   'Side allocations method, see wiki for allowed values',                'balance')),
    ('draw_pairing_method',         (str,   'Pairing method, see wiki for allowed values',                         'slide')),
    ('draw_avoid_conflicts',        (str,   'Conflict avoidance method, see wiki for allowed values',              'one_up_one_down')),
    ('draw_skip_adj_checkins',      (_bool, 'Automatically make all adjudicators available for all rounds',        False)),
    ('team_standings_rule',         (str,   'Rule for ordering teams, "australs" or "nz" or "wadl" see wiki',      'australs')),
    ('adj_conflict_penalty',        (int,   'Penalty for adjudicator-team conflict',                               1000000)),
    ('adj_history_penalty',         (int,   'Penalty for adjudicator-team history',                                10000)),
    ('avoid_same_institution',      (_bool, 'Avoid team-team institution conflicts in draw?',                      True)),
    ('avoid_team_history',          (_bool, 'Avoid team-team history conflicts in draw?',                          True)),
    ('team_institution_penalty',    (int,   'Penalty for team-team institution conflict',                          1)),
    ('team_history_penalty',        (int,   'Penalty for team-team history conflict',                              1000)),
    ('show_emoji',                  (_bool, 'Shows Emoji in the draw UI',                                          True)),
    ('show_institutions',           (_bool, 'Shows the institutions column in draw and other UIs',                 True)),
    ('show_novices',                (_bool, 'Show if a speaker is a novice',                                       False)),
    ('show_unaccredited',           (_bool, 'Show if an adjudicator is a novice (unaccredited)',                   False)),
    ('show_speakers_in_draw',       (_bool, 'Disable/Enable a hover element showing each teams speakers in the UI',True)),
    ('public_participants',         (_bool, 'Public interface to see all participants',                            False)),
    ('public_side_allocations',     (_bool, 'Public interface to see side pre-allocations',                        False)),
    ('public_draw',                 (_bool, 'Public interface to see RELEASED draws',                              False)),
    ('show_all_draws',              (_bool, 'If showing public draws, show all (past & future) RELEASED draws',    False)),
    ('public_motions',              (_bool, 'Public interface to see RELEASED motions',                            False)),
    ('public_motions_descending',   (_bool, 'List motions by round in descending order (as opposed to ascending)', True)),
    ('public_results',              (_bool, 'Public interface to see results from previous rounds',                False)),
    ('show_splitting_adjudicators', (_bool, 'If showing public results, show splitting adjudicators',              False)),
    ('show_motions_in_results',     (_bool, 'If showing public results, show motions with results',                False)),
    ('public_divisions',            (_bool, 'Public interface to see divisions',                                   False)),
    ('public_team_standings',       (_bool, 'Public interface to see team standings DURING tournament',            False)),
    ('public_breaking_teams',       (_bool, 'Public interface to see breaking teams',                              False)),
    ('public_breaking_adjs',        (_bool, 'Public interface to see breaking adjudicators',                       False)),
    ('public_ballots',              (_bool, 'Public interface to add ballots',                                     False)),
    ('public_feedback',             (_bool, 'Public interface to add feedback',                                    False)),
    ('public_use_password',         (_bool, 'Require password to submit public feedback and ballots',              False)),
    ('public_password',             (str,   'Value of the password for public submissions',                        ' ')),
    ('panellist_feedback_enabled',  (_bool, 'Allow public feedback to be submitted by panellists',                 True)),
    ('feedback_progress',           (_bool, 'Public interface to show who has unsubmitted ballots',                False)),
    ('tab_released',                (_bool, 'Displays the tab PUBLICLY. For AFTER the tournament',                 False)),
    ('motion_tab_released',         (_bool, 'Displays the motions tab PUBLICLY. For AFTER the tournament',         False)),
    ('ballots_released',            (_bool, 'Displays ballots PUBLICLY. For AFTER the tournament',                 False)),
    ('enable_flagged_motions',      (_bool, 'Allow particular motions to be flagged as contentious',               False)),
    ('enable_adj_notes',            (_bool, 'Enables a general-purpose notes field for adjudicators',              False)),
    ('enable_venue_groups',         (_bool, 'Enables the display of a venues grouping',                            False)),
    ('enable_venue_times',          (_bool, 'Enables dates and times to be set for venues',                        False)),
    ('enable_venue_overlaps',       (_bool, 'Allow and automatically debates to be placed in the first room',      False)),
    ('share_adjs',                  (_bool, 'Display adjudicators from other tournaments',                         False)),
    ('duplicate_adjs',              (_bool, 'Allow each adjudicator to be allocated to multiple rooms',            False)),
    ('enable_assistant_confirms',   (_bool, 'Enables Assistant users to confirm their own ballots',                False)),
    ('show_avg_margin',             (_bool, 'Enables a display of average margins in the team standings',          False)),
    ('margin_includes_dissenters',  (_bool, 'Whether a teams winning margin includes dissenting adj scores',       False)),
    ('team_points_rule',            (str,   'Normally 1 win = 1 point, "wadl" uses 2/1/0 for win/loss/forfeit',    'normal')),
    ('enable_divisions',            (_bool, 'Enables the sorting and display of teams into divisions',             False)),
    ('enable_postponements',        (_bool, 'Enables debates to have their status set to postponed',               False)),
    ('enable_forfeits',             (_bool, 'Enables one side of a debate to be in forfeit',                       False)),
    ('enable_division_motions',     (_bool, 'Enables assigning motions to a division',                             False)),
    ('minimum_division_size',       (int,   'Smallest allowed size for a division',                                5)),
    ('ideal_division_size',         (int,   'Ideal size for a division',                                           6)),
    ('maximum_division_size',       (int,   'Largest allowed size for a division',                                 8)),
])

BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

class Config(object):
    def __init__(self, tournament):
        self._t = tournament

    def __getattr__(self, key):
        return self.get(key)

    def get(self, key, default=None):
        from debate.models import Config
        if key in SETTINGS:
            coerce, help, _default = SETTINGS[key]
            default = default or _default
            value = Config.objects.get_(self._t, key, default)
            try:
                return coerce(value)
            except TypeError:
                print("Warning: Could not interpret configuration {key}: {value}, using {default} instead".format(
                    key=key, value=value, default=default))
                return default
        else:
            raise KeyError("Setting {0} does not exist.".format(key))

    def set(self, key, value):
        from debate.models import Config
        if key in SETTINGS:
            Config.objects.set(self._t, key, str(value))
        else:
            raise KeyError("Setting {0} does not exist.".format(key))

def make_config_form(tournament, data=None):
    from django import forms

    def _field(t, help):
        if t is int:
            return forms.IntegerField(help_text=help)
        elif t is float:
            return forms.FloatField(help_text=help)
        elif t is str:
            return forms.CharField(help_text=help)
        elif t is _bool:
            return forms.BooleanField(help_text=help, widget=Select(choices=BOOL_CHOICES), required=False)
        else:
            raise TypeError

    fields = OrderedDict()
    initial_data = {}
    for name, (coerce, help, default) in SETTINGS.items():
        fields[name] = _field(coerce, help)
        fields[name].default = default
        initial_data[name] = tournament.config.get(name)

    class BaseConfigForm(forms.BaseForm):
        def save(self):
            for name in SETTINGS.keys():
                tournament.config.set(name, self.cleaned_data[name])

    klass = type('ConfigForm', (BaseConfigForm,), {'base_fields': fields})
    if not data:
        return klass(initial=initial_data)
    else:
        return klass(data)


