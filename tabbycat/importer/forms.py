import csv
import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from participants.models import Adjudicator, Institution, Speaker, Team

logger = logging.getLogger(__name__)
TEAM_SHORT_REFERENCE_LENGTH = Team._meta.get_field('short_reference').max_length


class ImportValidationError(ValidationError):

    def __init__(self, lineno, message, *args, **kwargs):
        message = _("line %(lineno)d: %(message)s") % {
            'lineno': lineno,
            'message': message
        }
        super().__init__(message, *args, **kwargs)


class NumberForEachInstitutionForm(forms.Form):
    """Form that presents one numeric field for each institution, for the user
    to indicate how many objects to create from that institution. This is used
    for importing teams and adjudicators."""

    def __init__(self, institutions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.institutions = institutions
        self._create_fields()

    def _create_fields(self):
        """Dynamically generate one integer field for each institution, for the
        user to indicate how many teams are from that institution."""
        for institution in self.institutions:
            label = _("%(name)s (%(code)s)") % {'name': institution.name, 'code': institution.code}
            self.fields['number_institution_%d' % institution.id] = forms.IntegerField(
                    min_value=0, label=label, required=False,
                    widget=forms.NumberInput(attrs={'placeholder': 0}))


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


# ==============================================================================
# Teams and adjudicators
# ==============================================================================


class BaseParticipantDetailsForm(forms.ModelForm):
    """Form for the formset used in the second step of the simple importer. As
    well as the usual functions for managing an instance, this model also allows
    for a hidden input as the institution (rather than a ModelChoiceField),
    manages the tournament separately.

    This doesn't do all common functionality. Subclasses must do the following:
        - Override save() to populate the tournament field, if applicable.
        - Ensure that 'institution' is the 'fields' attribute of the Meta class.
    """

    # This field protects against changes to the form between rendering and
    # submission, for example, if the user reloads the team details step in a
    # different tab with different numbers of teams/adjudicators. Putting the
    # institution ID in a hidden field makes the client send it with the form,
    # keeping the information in a submission consistent.
    institution = forms.ModelChoiceField(queryset=Institution.objects.all(),
            widget=forms.HiddenInput)

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tournament = tournament

        # Grab an `institution_for_display` to help render the form. This is
        # not used anywhere in the form logic.
        institution_id = self.initial.get('institution')
        if institution_id is None:
            institution_id = self.data.get(self.add_prefix('institution'))
        try:
            self.institution_for_display = Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            logger.error("Could not find institution from initial or data")

    def validate_unique(self):
        """Overrides ModelForm.validate_unique to include tournament in the check."""
        exclude = self._get_validation_exclusions()
        if 'tournament' in exclude:
            exclude.remove('tournament')
        self.instance.tournament = self.tournament
        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError as e:
            self._update_errors(e)


class TeamDetailsForm(BaseParticipantDetailsForm):
    """Adds provision for a textarea input for speakers."""

    speakers = forms.CharField(required=True) # widget is set in form constructor

    class Meta:
        model = Team
        fields = ('reference', 'use_institution_prefix', 'institution')
        labels = {
            'reference': _("Name (excluding institution name)"),
            'use_institution_prefix': _("Prefix team name with institution name?"),
        }

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(tournament, *args, **kwargs)

        # Set speaker widget to match tournament settings
        nspeakers = tournament.pref('substantive_speakers')
        self.fields['speakers'].widget = forms.Textarea(attrs={'rows': nspeakers,
                'placeholder': _("One speaker's name per line")})
        self.initial.setdefault('speakers', "\n".join(
                _("Speaker %d") % i for i in range(1, nspeakers+1)))

    def clean_speakers(self):
        # Split into list of names, removing blank lines.
        names = self.cleaned_data['speakers'].split('\n')
        names = [name.strip() for name in names]
        names = [name for name in names if name]
        if len(names) == 0:
            self.add_error('speakers', _("There must be at least one speaker."))
        return names

    def _post_clean_speakers(self):
        """Validates the Speaker instances that would be created."""
        for name in self.cleaned_data.get('speakers', []):
            try:
                speaker = Speaker(name=name)
                speaker.full_clean(exclude=('team',))
            except ValidationError as errors:
                for field, e in errors: # replace field with `speakers`
                    self.add_error('speakers', e)

    def _post_clean(self):
        super()._post_clean()
        self._post_clean_speakers()

    def save(self, commit=True):
        # First save the team, then create the speakers
        team = super().save(commit=False)
        team.short_reference = team.reference[:TEAM_SHORT_REFERENCE_LENGTH]
        team.tournament = self.tournament

        if commit:
            team.save()
            for name in self.cleaned_data['speakers']:
                team.speaker_set.create(name=name)

        return team


class AdjudicatorDetailsForm(BaseParticipantDetailsForm):
    """Also provides for the boolean 'shared' field, which indicates that the
    adjudicator should not be attached to a tournament."""

    shared = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = Adjudicator
        fields = ('name', 'test_score', 'institution')
        labels = {
            'test_score': _("Rating"),
        }

    def save(self, commit=True):
        # First save the team, then create the speakers
        adjudicator = super().save(commit=False)
        adjudicator.tournament = None if self.cleaned_data.get('shared', False) else self.tournament
        if commit:
            adjudicator.save()
        return adjudicator
