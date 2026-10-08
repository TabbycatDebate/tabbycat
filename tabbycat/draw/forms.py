from django import forms
from django.utils.translation import gettext as _


class ConfirmDrawDeletionForm(forms.Form):
    round_name = forms.CharField(label=_("Full round name"), required=True)
    overwrite_preformed_panels = forms.BooleanField(
        label=_("Overwrite preformed panels with current panels"),
        required=False,
    )

    def __init__(self, round, **kwargs):
        self.round = round
        super().__init__(**kwargs)

    def clean_round_name(self):
        if self.cleaned_data['round_name'] != self.round.name:
            raise forms.ValidationError(_("You must type '%s' to confirm draw and results deletion.") % self.round.name)
