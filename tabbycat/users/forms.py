from django.contrib.auth.forms import UserCreationForm
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
