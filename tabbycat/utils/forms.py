from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _


class OptionalChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(OptionalChoiceField, self).__init__(*args, **kwargs)
        self.choices = [(None, '---------')] + list(self.choices)


# class BaseEligibilityForm(forms.Form):
#     """Sets which teams are eligible for some category."""

#     categories_field_name = None

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._create_and_initialise_fields()

#     def get_instance_queryset(self):
#         raise NotImplementedError

#     def get_category_queryset(self):
#         raise NotImplementedError

#     @staticmethod
#     def _fieldname_eligibility(instance):
#         return 'eligibility_%(instance)d' % {'instance': instance.pk}

#     def _create_and_initialise_fields(self):
#         """Dynamically generate fields, one ModelMultipleChoiceField for each instance."""
#         categories_queryset = self.get_category_queryset()

#         for instance in self.get_instance_queryset():
#             self.fields[self._fieldname_eligibility(instance)] = forms.ModelMultipleChoiceField(
#                 queryset=categories_queryset, widget=forms.CheckboxSelectMultiple, required=False)
#             self.initial[self._fieldname_eligibility(instance)] = getattr(instance, self.categories_field_name).all()

#     def save(self):
#         for instance in self.get_instance_queryset():
#             setattr(instance, self.categories_field_name, self.cleaned_data[self._fieldname_eligibility(instance)])
#             instance.save()

#     def instance_iter(self):
#         for instance in self.get_instance_queryset():
#             yield instance, self[self._fieldname_eligibility(instance)]


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
