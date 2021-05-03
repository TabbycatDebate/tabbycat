from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class TabRegistrationForm(UserCreationForm):

    class Meta:
        model = User

        fields = ('email', 'username')

    def save(self, commit=True):
        user = super(TabRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user
