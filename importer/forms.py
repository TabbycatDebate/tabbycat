from django import forms
from django.utils.translation import ugettext as _

class AddInstitutionsForm(forms.Form):

    def clean(self, value):
        value = super(AddInstitutionsForm, self).clean(value)
        print("testting value")
        print(value)
        return value

    pass

class AddTeamsForm(forms.Form):
    pass

class AddVenuesForm(forms.Form):
    pass

class AddAdjudicatorsForm(forms.Form):
    pass
