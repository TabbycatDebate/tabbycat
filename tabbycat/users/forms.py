from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm, UsernameField
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


class InviteUserForm(PasswordResetForm):
    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)

        self.fields['role'] = forms.ModelChoiceField(queryset=tournament.group_set.all())

    def get_users(self, email):
        user, created = get_user_model().objects.get_or_create(
            email=email,
            defaults={
                'username': email.split("@")[0],
            },
        )
        user.membership_set.create(group=self.cleaned_data['role'])
        return [user]

    def save(self, *args, **kwargs):
        kwargs['extra_email_context'] = {**(kwargs['extra_email_context'] or {}), 'tournament': self.tournament}
        return super().save(*args, **kwargs)


class AcceptInvitationForm(SetPasswordForm):
    username = UsernameField(label=_("Username"), help_text=get_user_model()._meta.get_field('username').help_text)

    field_order = ('username', 'new_password1', 'new_password2')

    def save(self, commit=True):
        self.user.username = self.cleaned_data['username']
        return super().save(commit=commit)
