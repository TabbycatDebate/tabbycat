from django.utils.datastructures import SortedDict

#name,  coerce, help, default
SETTINGS = SortedDict([
    ('score_min', (int, 'Minimum allowed score', 65)),
    ('score_max', (int, 'Maximum allowed score', 85)),
    ('reply_score_min', (int, 'Minimum allowed reply score', 30)),
    ('reply_score_max', (int, 'Maximum allowed reply score', 45)),
])


class Config(object):
    def __init__(self, tournament):
        self._t = tournament

    def __getattr__(self, key):
        return self.get(key)

    def get(self, key):
        from debate.models import Config
        if key in SETTINGS:
            coerce, help, default = SETTINGS[key]
            return Config.objects.get_(self._t, key, default)
    
    def set(self, key, value):
        from debate.models import Config
        Config.objects.set(self._t, key, value)


def make_config_form(tournament, data=None):
    from django import forms

    def _field(t):
        if t is int:
            return forms.IntegerField

    fields = SortedDict()
    initial_data = {}
    for name, (coerce, help, default) in SETTINGS.items():
        fields[name] = _field(coerce)(help_text=help)
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


