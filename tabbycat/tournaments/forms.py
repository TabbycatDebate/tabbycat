from django.forms.fields import IntegerField
from django.forms import ModelForm

from .models import Tournament
from .utils import auto_make_finals_rounds, auto_make_rounds

from breakqual.models import BreakCategory


class TournamentForm(ModelForm):

    class Meta:
        model = Tournament
        fields = ('name', 'short_name', 'slug')

    num_prelim_rounds = IntegerField(
        min_value=1,
        label="Number of preliminary rounds")
    num_final_rounds = IntegerField(
        min_value=1,
        required=False,
        label="Number of finals rounds",
        help_text="Leave blank if there are no finals rounds")

    break_size = IntegerField(
        min_value=2,
        required=False,
        label="Number of teams in the open break",
        help_text="Leave blank if there are no finals rounds")

    def save(self):
        tournament = super(TournamentForm, self).save()
        auto_make_rounds(tournament, self.cleaned_data["num_prelim_rounds"])

        if self.cleaned_data["break_size"]:
            open_break = BreakCategory(
                tournament=tournament,
                name="Open",
                slug="open",
                seq=1,
                break_size=self.cleaned_data["break_size"],
                is_general=True,
                priority=100
            ).save()
        else:
            open_break = None

        if self.cleaned_data["num_final_rounds"]:
            auto_make_finals_rounds(tournament,
                self.cleaned_data["num_prelim_rounds"],
                self.cleaned_data["num_final_rounds"], open_break)

        tournament.current_round = tournament.round_set.first()
        tournament.save()
        return tournament
