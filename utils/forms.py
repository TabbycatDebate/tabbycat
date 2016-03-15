from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import UserCreationForm


class OptionalChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(OptionalChoiceField, self).__init__(*args, **kwargs)
        self.choices = [(None, '---------')] + list(self.choices)


class SuperuserCreationForm(UserCreationForm):
    """A form that creates a superuser from the given username and password."""

    def save(self, commit=True):
        user = super(SuperuserCreationForm, self).save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user
