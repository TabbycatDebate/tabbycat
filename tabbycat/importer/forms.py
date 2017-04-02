import csv

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from participants.models import Institution, Speaker, Team

TEAM_SHORT_REFERENCE_LENGTH = Team._meta.get_field('short_reference').max_length


class ImportValidationError(ValidationError):

    def __init__(self, lineno, message, *args, **kwargs):
        message = _("line %(lineno)d: %(message)s") % {
            'lineno': lineno,
            'message': message
        }
        super().__init__(message, *args, **kwargs)


# ==============================================================================
# Institutions
# ==============================================================================

class ImportInstitutionsRawForm(forms.Form):
    """Form that takes in a CSV-style list of institutions, splits it and stores
    the split data."""

    institutions_raw = forms.CharField(widget=forms.Textarea(attrs={'rows': 20}))

    def clean_institutions_raw(self):
        lines = self.cleaned_data['institutions_raw'].split('\n')
        errors = []
        institutions = []

        for i, line in enumerate(csv.reader(lines), start=1):
            if len(line) < 1:
                continue # skip blank lines
            if len(line) < 2:
                errors.append(ImportValidationError(i,
                    _("This line (for %(institution)s) didn't have a code") %
                    {'institution': line[0]}))
                continue
            if len(line) > 2:
                errors.append(ImportValidationError(i,
                    _("This line (for %(institution)s) had too many columns") %
                    {'institution': line[0]}))

            line = [x.strip() for x in line]
            institutions.append({'name': line[0], 'code': line[1]})

        if errors:
            raise ValidationError(errors)

        return institutions


class InstitutionForm(forms.ModelForm):

    class Meta:
        model = Institution
        fields = ('name', 'code')


# ==============================================================================
# Teams
# ==============================================================================

class ImportTeamsNumbersForm(forms.Form):
    """Form that presents one numeric field for each institution, for the user
    to indicate how many teams are from that institution."""

    def __init__(self, institutions, *args, **kwargs):
        self.institutions = institutions
        super().__init__(*args, **kwargs)
        self._create_fields()

    def _create_fields(self):
        """Dynamically generate one integer field for each institution, for the
        user to indicate how many teams are from that institution."""
        for institution in self.institutions:
            label = _("%(name)s (%(code)s)") % {'name': institution.name, 'code': institution.code}
            self.fields['number_institution_%d' % institution.id] = forms.IntegerField(
                    min_value=0, label=label, widget=forms.NumberInput(attrs={'placeholder': 0}))


class TeamDetailsForm(forms.ModelForm):

    # The purpose of the institution field is to protect against changes in
    # the form between rendering and submission, for example, if the user
    # reloads the team details step in a different tab with different numbers
    # of teams. Putting the institution ID in a hidden field makes the client
    # send it with the form, keeping the information in a submission consistent.
    institution = forms.ModelChoiceField(queryset=Institution.objects.all(),
            widget=forms.HiddenInput)

    speakers = forms.CharField(widget=forms.Textarea(attrs={'rows': 3,
            'placeholder': ugettext_lazy("Speaker 1\nSpeaker 2\nSpeaker 3")}))

    class Meta:
        model = Team
        fields = ('reference', 'use_institution_prefix', 'institution')
        labels = {
            'reference': _("Name (excluding institution name)"),
            'use_institution_prefix': _("Prefix team name with institution name?"),
        }

    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)

        # Set speaker widget to match tournament settings
        nspeakers = tournament.pref('substantive_speakers')
        self.fields['speakers'].widget = forms.Textarea(attrs={'rows': nspeakers})
        self.initial.setdefault('speakers', "\n".join(
                _("Speaker %d") % i for i in range(1, nspeakers+1)))

        # Grab an `institution_for_display` to help render the form. This is
        # not used anywhere in the form logic.
        institution_id = self.initial['institution']
        self.institution_for_display = Institution.objects.get(id=institution_id)

    def clean_speakers(self):
        # Split into list of names, removing blank lines.
        names = self.cleaned_data['speakers'].split('\n')
        names = [name.strip() for name in names]
        return [name for name in names if name]

    def _post_clean_speakers(self):
        """Validates the Speaker instances that would be created."""
        for name in self.cleaned_data['speakers']:
            try:
                speaker = Speaker(name=name, team=self.instance)
                speaker.full_clean()
            except ValidationError as errors:
                for field, e in errors: # replace field with `speakers`
                    self.add_error('speakers', e)

    def _post_clean(self):
        super()._post_clean()
        self._post_clean_speakers()

    def save(self):
        # First save the team, then create the speakers
        team = super().save(commit=False)
        team.short_reference = team.reference[:TEAM_SHORT_REFERENCE_LENGTH]
        team.tournament = self.tournament
        team.institution_id = self.cleaned_data['institution_id']
        team.save()

        for name in self.cleaned_data['speakers']:
            team.speaker_set.create(name=name)

        return team
