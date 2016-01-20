from django import forms
from django.utils.translation import ugettext as _

class OptionalChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(OptionalChoiceField, self).__init__(*args, **kwargs)
        self.choices = [(None, '---------')] + list(self.choices)
