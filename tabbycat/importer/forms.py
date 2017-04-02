import csv

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from participants.models import Institution

class ImportValidationError(ValidationError):

    def __init__(self, lineno, message, *args, **kwargs):
        message = _("line %(lineno)d: %(message)s") % {
            'lineno': lineno,
            'message': message
        }
        super().__init__(message, *args, **kwargs)


class ImportInstitutionsRawForm(forms.Form):
    """Form that takes in a CSV-style list of institutions, splits it and stores
    the split data."""

    institutions_raw = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'cols': 80}))

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
