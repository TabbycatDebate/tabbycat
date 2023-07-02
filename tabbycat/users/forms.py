from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.utils.translation import gettext_lazy as _


class SuperuserCreationForm(UserCreationForm):
    """A form that creates a superuser from the given username and password."""

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")
        labels = {"email": _("Email address")}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user


class TabRegistrationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")
        labels = {"email": _("Email address")}


class InviteUserForm(PasswordResetForm):
    role = forms.ChoiceField(label=_("User role"), choices=(
        ('assistant', _("Assistant")),
        ('administrator', _("Administrator")),
    ))

    def get_users(self, email):
        user, created = get_user_model().objects.get_or_create(
            email=email,
            defaults={
                'is_superuser': self.cleaned_data['role'] == 'administrator',
                'username': email.split("@")[0],
            },
        )
        return [user]
