from django.forms.fields import IntegerField
from django.forms import ModelForm
from .models import Tournament
from .utils import auto_make_rounds

class TournamentForm(ModelForm):

    class Meta:
        model = Tournament
        fields = ('name', 'short_name', 'slug')

    num_prelim_rounds = IntegerField(min_value=1, label="Number of preliminary rounds")

    def save(self):
        tournament = super(TournamentForm, self).save()
        auto_make_rounds(tournament, self.cleaned_data["num_prelim_rounds"])
        tournament.current_round = tournament.round_set.first()
        tournament.save()
        return tournament
