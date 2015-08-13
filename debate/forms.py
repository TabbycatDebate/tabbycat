from django import forms
from django.utils.translation import ugettext as _

# TODO: move to a more general forms.py? is used by breaking+feedback
class OptionalChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(OptionalChoiceField, self).__init__(*args, **kwargs)
        self.choices = [(None, '---------')] + list(self.choices)
