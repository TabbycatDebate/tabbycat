from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _


class OptionalChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(OptionalChoiceField, self).__init__(*args, **kwargs)
        self.choices = [(None, '---------')] + list(self.choices)


class SuperuserCreationForm(UserCreationForm):
    """A form that creates a superuser from the given username and password."""

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")
        labels = {"email": _("E-mail address")}

    def save(self, commit=True):
        user = super(SuperuserCreationForm, self).save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user
