from collections import OrderedDict
from django import forms

from .models import Option

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

    # TODO: below items need to rework the way BaseScoreField is past config variables
    ('score_min',                   (float, 'Minimum allowed score',                                               68)),
    ('score_max',                   (float, 'Maximum allowed score',                                               82)),
    ('score_step',                  (float, 'Score steps allowed',                                                 1)),
    ('reply_score_min',             (float, 'Minimum allowed reply score',                                         34)),
    ('reply_score_max',             (float, 'Maximum allowed reply score',                                         41)),
    ('reply_score_step',            (float, 'Reply score steps allowed',                                           0.5)),

    # TODO: below options need a rework of the way OPTIONS_TO_CONFIG_MAPPING works
    ('draw_side_allocations',       (str,   'Side allocations method, see wiki for allowed values',                'balance')),
    ('draw_pairing_method',         (str,   'Pairing method, see wiki for allowed values',                         'slide')),
    ('draw_avoid_conflicts',        (str,   'Conflict avoidance method, see wiki for allowed values',              'one_up_one_down')),
    ('team_institution_penalty',    (int,   'Penalty for team-team institution conflict',                          1)),
    ('avoid_same_institution',      (_bool, 'Avoid team-team institution conflicts in draw?',                      True)),
    ('avoid_team_history',          (_bool, 'Avoid team-team history conflicts in draw?',                          True)),
    ('team_history_penalty',        (int,   'Penalty for team-team history conflict',                              1000)),
    ('draw_odd_bracket',            (str,   'Odd bracket resolution method, see wiki for allowed values',          'intermediate_bubble_up_down')),

    # CHeck other OPTIONS_TO_CONFIG_MAPPING, such as 321-324 of tournament models


])

BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

class Config(object):
    def __init__(self, tournament):
        self._t = tournament

    def __getattr__(self, key):
        try:
            return self.get(key)
        except KeyError:
            raise AttributeError(key)

    def get(self, key, default=None):
        if key in SETTINGS:
            coerce, help, _default = SETTINGS[key]
            default = default or _default
            value = Option.objects.get_(self._t, key, default)
            try:
                return coerce(value)
            except TypeError:
                print("Warning: Could not interpret configuration {key}: {value}, using {default} instead".format(
                    key=key, value=value, default=default))
                return default
        else:
            raise KeyError("Setting {0} does not exist.".format(key))

    def set(self, key, value):

        if key in SETTINGS:
            Option.objects.set(self._t, key, str(value))
        else:
            raise KeyError("Setting {0} does not exist.".format(key))

def make_options_form(tournament, data=None):

    def _field(t, help):
        if t is int:
            return forms.IntegerField(help_text=help)
        elif t is float:
            return forms.FloatField(help_text=help)
        elif t is str:
            return forms.CharField(help_text=help)
        elif t is _bool:
            return forms.BooleanField(help_text=help, widget=forms.Select(choices=BOOL_CHOICES), required=False)
        else:
            raise TypeError

    fields = OrderedDict()
    initial_data = {}
    for name, (coerce, help, default) in list(SETTINGS.items()):
        fields[name] = _field(coerce, help)
        fields[name].default = default
        initial_data[name] = tournament.config.get(name)

    class BaseConfigForm(forms.BaseForm):
        def save(self):
            for name in list(SETTINGS.keys()):
                tournament.config.set(name, self.cleaned_data[name])

    klass = type('ConfigForm', (BaseConfigForm,), {'base_fields': fields})
    if not data:
        return klass(initial=initial_data)
    else:
        return klass(data)
