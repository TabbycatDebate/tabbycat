import csv
import logging
from itertools import zip_longest

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext as _, ngettext, ngettext_lazy

from participants.models import Adjudicator, Institution, Speaker, Team
from venues.models import Venue

logger = logging.getLogger(__name__)
TEAM_SHORT_REFERENCE_LENGTH = Team._meta.get_field('short_reference').max_length

# There are 7 fields for formset/wizard management and CSRF detection
MAX_FORM_DATA_FIELDS = settings.DATA_UPLOAD_MAX_NUMBER_FIELDS - 7


class ImportValidationError(ValidationError):

    def __init__(self, lineno, message, *args, **kwargs):
        message = _("line %(lineno)d: %(message)s") % {
            'lineno': lineno,
            'message': message,
        }
        super().__init__(message, *args, **kwargs)


# ==============================================================================
# Raw forms (CSV-style import)
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

        if len(institutions) == 0:
            raise ValidationError(_("There were no institutions to import."))

        max_allowed = MAX_FORM_DATA_FIELDS // 3  # 3 fields: 'name', 'code', 'id'.
        if len(institutions) > max_allowed:
            raise ValidationError(ngettext(
                "Sorry, you can only import up to %(max_allowed)d institution at a "
                "time. (You currently have %(given)d.) "
                "Try splitting your import into smaller chunks.",
                "Sorry, you can only import up to %(max_allowed)d institutions at a "
                "time. (You currently have %(given)d.) "
                "Try splitting your import into smaller chunks.",
                max_allowed) % {'max_allowed': max_allowed, 'given': len(institutions)})

        return institutions


class ImportVenuesRawForm(forms.Form):
    """Form that takes in a CSV-style list of venues, splits it and stores the
    split data."""

    venues_raw = forms.CharField(widget=forms.Textarea(attrs={'rows': 20}))

    def clean_venues_raw(self):
        lines = self.cleaned_data['venues_raw'].split('\n')
        venues = []

        for i, line in enumerate(csv.reader(lines), start=1):
            if len(line) < 1:
                continue # skip blank lines
            params = {}
            params['name'] = line[0]
            params['priority'] = line[1] if len(line) > 1 else '100'

            params = {k: v.strip() for k, v in params.items()}
            venues.append(params)

        if len(venues) == 0:
            raise ValidationError(_("There were no rooms to import."))

        max_allowed = MAX_FORM_DATA_FIELDS // (len(VenueDetailsForm.base_fields) + 1)
        if len(venues) > max_allowed:
            raise ValidationError(ngettext(
                "Sorry, you can only import up to %(max_allowed)d room at a "
                "time. (You currently have %(given)d.) "
                "Try splitting your import into smaller chunks.",
                "Sorry, you can only import up to %(max_allowed)d rooms at a "
                "time. (You currently have %(given)d.) "
                "Try splitting your import into smaller chunks.",
                max_allowed) % {'max_allowed': max_allowed, 'given': len(venues)})

        return venues


# ==============================================================================
# Details forms
# ==============================================================================

class BaseTournamentObjectDetailsForm(forms.ModelForm):
    """Form for the formset used in the second step of the simple importer. As
    well as the usual functions for managing an instance, this model also
    manages the tournament separately.

    This doesn't do everything. Subclasses must override save() to populate the
    tournament field, if applicable.
    """

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament

    def _get_validation_exclusions(self):
        exclude = super()._get_validation_exclusions()
        if 'tournament' in exclude:
            exclude.remove('tournament')
        return exclude

    def full_clean(self):
        self.instance.tournament = self.tournament
        return super().full_clean()


class VenueDetailsForm(BaseTournamentObjectDetailsForm):

    class Meta:
        model = Venue
        fields = ('name', 'priority')


class BaseInstitutionObjectDetailsForm(BaseTournamentObjectDetailsForm):
    """Adds a hidden input for the institution and automatic detection of the
    institution from initial or data.

    Subclasses must ensure that `'institution'` is in the `fields` attribute
    of the Meta class.
    """

    # This field protects against changes to the form between rendering and
    # submission, for example, if the user reloads the team details step in a
    # different tab with different numbers of teams/adjudicators. Putting the
    # institution ID in a hidden field makes the client send it with the form,
    # keeping the information in a submission consistent.
    institution = forms.ModelChoiceField(queryset=Institution.objects.all(),
                                         widget=forms.HiddenInput, required=False)

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(tournament, *args, **kwargs)

        # Grab an `institution_for_display` to help render the form. This is
        # not used anywhere in the form logic. First try `initial` (for when
        # the form is initially rendered), then try `data` (for when the form
        # is rerendered after a validation error).
        institution_id = self.initial.get('institution') or self.data.get(self.add_prefix('institution'))

        if institution_id:
            try:
                self.institution_for_display = Institution.objects.get(id=institution_id)
            except Institution.DoesNotExist:
                logger.exception("Could not find institution from initial or data")
        else:
            self.institution_for_display = None


class TeamDetailsForm(BaseInstitutionObjectDetailsForm):
    """Adds provision for a textarea input for speakers."""

    speakers = forms.CharField(required=True, label=_("Speakers' names")) # widget is set in form constructor
    emails = forms.CharField(required=False, label=_("Speakers' email addresses"),
        help_text=_("Optional, useful to include if distributing private URLs, list in same order as speakers' names")) # widget is set in form constructor
    short_reference = forms.CharField(widget=forms.HiddenInput, required=False) # doesn't actually do anything, just placeholder to avoid validation failure

    class Meta:
        model = Team
        fields = ('reference', 'short_reference', 'use_institution_prefix', 'institution')
        labels = {
            'reference': _("Name (excluding institution name)"),
            'use_institution_prefix': _("Prefix team name with institution name?"),
        }
        help_texts = {
            'reference': _("Do not include institution name (check the \"Prefix team name with institution name?\" field instead)"),
        }

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(tournament, *args, **kwargs)

        if self.institution_for_display is None:
            self.initial['use_institution_prefix'] = False
            self.fields['use_institution_prefix'].disabled = True
            self.fields['use_institution_prefix'].help_text = _("(Not applicable to unaffiliated teams)")

        # Set speaker and email widgets to match tournament settings
        nspeakers = tournament.pref('substantive_speakers')
        self.fields['speakers'].widget = forms.Textarea(attrs={'rows': nspeakers,
                'placeholder': _("One speaker's name per line")})
        self.fields['speakers'].help_text = _("Can be separated by newlines, tabs or commas")
        self.initial.setdefault('speakers', "\n".join(
                _("Speaker %d") % i for i in range(1, nspeakers+1)))
        self.fields['emails'].widget = forms.Textarea(attrs={'rows': nspeakers,
                'placeholder': "\n".join(_("speaker%d@example.edu") % i for i in range(1, nspeakers+1))})

    @staticmethod
    def _split_lines(data):
        """Split into list of names or emails; removing blank lines."""
        items = data.replace('\t', '\n').replace(',', '\n')
        items = items.split('\n')
        items = [item.strip() for item in items]
        items = [item for item in items if item]
        return items

    def clean_speakers(self):
        names = self._split_lines(self.cleaned_data['speakers'])
        if len(names) == 0:
            self.add_error('speakers', _("There must be at least one speaker."))
        return names

    def clean_emails(self):
        emails = self._split_lines(self.cleaned_data['emails'])
        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                self.add_error('emails', _("%(email)s is not a valid email address.") % {'email': email})
        return emails

    def clean_short_reference(self):
        # Ignore the actual field value, and replace with the (long) reference.
        # The purpose of this is to ensure that this field is populated, because
        # Team.clean() checks it, so it can't just be excluded using `exclude=`.
        reference = self.cleaned_data.get('reference', '')
        return reference[:TEAM_SHORT_REFERENCE_LENGTH]

    def clean(self):
        super().clean()
        if len(self.cleaned_data.get('emails', [])) > len(self.cleaned_data.get('speakers', [])):
            self.add_error('emails', _("There are more email addresses than speakers."))

    def _post_clean_speakers(self):
        """Validates the Speaker instances that would be created."""
        for i, name in enumerate(self.cleaned_data.get('speakers', [])):
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
        team.tournament = self.tournament

        if commit:
            team.save()
            for name, email in zip_longest(self.cleaned_data['speakers'], self.cleaned_data['emails']):
                team.speaker_set.create(name=name, email=email)
            team.break_categories.set(team.tournament.breakcategory_set.filter(is_general=True))

            if team.institution:
                team.teaminstitutionconflict_set.create(institution=team.institution)

        return team


class TeamDetailsFormSet(forms.BaseModelFormSet):

    def get_unique_error_message(self, unique_check):
        # Overrides the base implementation
        if unique_check == ('reference', 'institution', 'tournament'):
            return _("Every team in a single tournament from the same institution must "
                "have a different name. Please correct the duplicate data.")
        else:
            return super().get_unique_error_message(unique_check)


class AdjudicatorDetailsForm(BaseInstitutionObjectDetailsForm):

    class Meta:
        model = Adjudicator
        fields = ('name', 'base_score', 'institution', 'email')
        labels = {
            'base_score': _("Rating"),
        }

    def clean_base_score(self):
        base_score = self.cleaned_data['base_score']
        min_score = self.tournament.pref('adj_min_score')
        max_score = self.tournament.pref('adj_max_score')
        if base_score < min_score or max_score < base_score:
            self.add_error('base_score', _("This value must be between %(min)d and %(max)d.") %
                {'min': min_score, 'max': max_score})
        return base_score

    def save(self, commit=True):
        adj = super().save(commit=commit)
        if commit and adj.institution:
            adj.adjudicatorinstitutionconflict_set.create(institution=adj.institution)
        return adj


# ==============================================================================
# Numbers forms
# ==============================================================================
# These reference the details forms, so must come after them.

class BaseNumberForEachInstitutionForm(forms.Form):
    """Form that presents one numeric field for each institution, for the user
    to indicate how many objects to create from that institution. This is used
    for importing teams and adjudicators."""

    number_unaffiliated = forms.IntegerField(min_value=0, required=False,
        label=_("Unaffiliated (no institution)"),
        widget=forms.NumberInput(attrs={'placeholder': 0}))

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

    def clean(self):
        super().clean()

        given = self.cleaned_data.get('number_unaffiliated') or 0  # data might be None
        for institution in self.institutions:
            given += self.cleaned_data.get('number_institution_%d' % institution.id) or 0  # data might be None
        max_allowed = MAX_FORM_DATA_FIELDS // self.num_detail_fields
        if given > max_allowed:
            raise ValidationError(self.too_many_error_message % {
                'max_allowed': max_allowed, 'given': given})


class ImportTeamsNumbersForm(BaseNumberForEachInstitutionForm):

    num_detail_fields = len(TeamDetailsForm.base_fields) + 1
    too_many_error_message = ngettext_lazy(
        "Sorry, you can only import up to %(max_allowed)d team at a time. "
        "(These numbers currently add to %(given)d.) "
        "Try splitting your import into smaller chunks.",
        "Sorry, you can only import up to %(max_allowed)d teams at a time. "
        "(These numbers currently add to %(given)d.) "
        "Try splitting your import into smaller chunks.",
        'max_allowed')


class ImportAdjudicatorsNumbersForm(BaseNumberForEachInstitutionForm):

    num_detail_fields = len(AdjudicatorDetailsForm.base_fields) + 1
    too_many_error_message = ngettext_lazy(
        "Sorry, you can only import up to %(max_allowed)d adjudicator at a time. "
        "(These numbers currently add to %(given)d.) "
        "Try splitting your import into smaller chunks.",
        "Sorry, you can only import up to %(max_allowed)d adjudicators at a time. "
        "(These numbers currently add to %(given)d.) "
        "Try splitting your import into smaller chunks.",
        'max_allowed')
