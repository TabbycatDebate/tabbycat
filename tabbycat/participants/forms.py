from django import forms
from django.utils.translation import gettext as _


class ConfirmSpeakerDeletionForm(forms.Form):
    speaker_name = forms.CharField(label=_("Speaker's full name"), required=True)

    def __init__(self, *args, speaker=None, **kwargs):
        self.speaker = speaker
        super().__init__(*args, **kwargs)

    def clean_speaker_name(self):
        if self.cleaned_data['speaker_name'] != self.speaker.name:
            raise forms.ValidationError(
                _("You must type '%(name)s' exactly to confirm deletion.") % {'name': self.speaker.name},
            )
