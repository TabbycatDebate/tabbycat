from django.utils.datastructures import SortedDict

#name,  coerce, help, default
SETTINGS = SortedDict([
    ('score_min', (float, 'Minimum allowed score', 68)),
    ('score_max', (float, 'Maximum allowed score', 82)),
    ('score_step', (float, 'Score steps allowed', 1)),
    ('reply_score_min', (float, 'Minimum allowed reply score', 34)),
    ('reply_score_max', (float, 'Maximum allowed reply score', 41)),
    ('reply_score_step', (float, 'Reply score steps allowed', 0.5)),
    ('break_size', (int, 'Number of breaking teams', 16)),
    ('adj_min_score', (float, 'Minimum adjudicator score', 1.5)),
    ('adj_max_score', (float, 'Maximum adjudicator score', 5)),
    ('adj_chair_min_score', (float, 'Minimum chair score', 3.5)),
    ('adj_conflict_penalty', (int, 'Penalty for adjudicator-team conflict',
                              1000000)),
    ('adj_history_penalty', (int, 'Penalty for adjudicator-team history',
                              10000)),
    ('show_emoji', (int, 'Shows Emoji in the draw UI', 1)),
    ('show_institutions', (int, 'Shows the institutions column in the draw UI', 1)),
    ('public_participants', (int, 'Public interface to see all participants', 0)),
    ('public_draw', (int, 'Public interface to see RELEASED draws', 0)),
    ('public_ballots', (int, 'Public interface to add ballots', 0)),
    ('public_feedback', (int, 'Public interface to add feedback', 0)),
    ('feedback_progress', (int, 'Public interface to view unsubmitted ballots', 0)),
    ('tab_released', (int, 'Displays the tab PUBLICLY. For AFTER the tournament', 0)),
])


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
            return coerce(Config.objects.get_(self._t, key, default))
        else:
            return default

    def set(self, key, value):
        from debate.models import Config
        Config.objects.set(self._t, key, value)


def make_config_form(tournament, data=None):
    from django import forms

    def _field(t, help):
        if t is int:
            return forms.IntegerField(help_text=help)
        if t is float:
            return forms.FloatField(help_text=help)

    fields = SortedDict()
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


