import math

from django.forms.fields import IntegerField
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from breakqual.models import BreakCategory
from importer.management.commands import importtournament
from utils.forms import OptionalChoiceField

from .models import Tournament
from .utils import auto_make_break_rounds, auto_make_rounds


class TournamentForm(ModelForm):

    class Meta:
        model = Tournament
        fields = ('name', 'short_name', 'slug')

    num_prelim_rounds = IntegerField(
        min_value=1,
        label=_("Number of preliminary rounds"))

    break_size = IntegerField(
        min_value=2,
        required=False,
        label=_("Number of teams in the open break"),
        help_text=_("Leave blank if there are no break rounds."))

    import_options = OptionalChoiceField(
        label=_("Setup this tournament using demo data"), required=False,
        help_text=_("Import fake data for those testing/learning Tabbycat"),
        choices=[('demo_simple','Use simple demo data (for small tournaments)'),
                 ('demo',       'Use complex demo data (for big tournamens)')])

    def save(self):
        tournament = super(TournamentForm, self).save()
        auto_make_rounds(tournament, self.cleaned_data["num_prelim_rounds"])

        break_size = self.cleaned_data["break_size"]
        if break_size:
            open_break = BreakCategory(
                tournament=tournament,
                # Translators: This is the name given to the 'Open Break'.
                name=_("Open"),
                slug="open",
                seq=1,
                break_size=break_size,
                is_general=True,
                priority=100
            )
            open_break.full_clean()
            open_break.save()

            num_break_rounds = math.ceil(math.log2(break_size))
            auto_make_break_rounds(tournament, num_break_rounds, open_break)

        tournament.current_round = tournament.round_set.first()
        tournament.save()

        demo_import = self.cleaned_data["import_options"]
        if demo_import:
            print("Importing demo")
            management.call_command('importtournament', verbosity=0)

        return tournament
