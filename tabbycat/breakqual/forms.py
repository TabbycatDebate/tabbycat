from django import forms

from utils.forms import OptionalChoiceField

from .models import BreakingTeam


# ==============================================================================
# Breaking teams form
# ==============================================================================

class BreakingTeamsForm(forms.Form):
    """Updates the remarks on breaking teams and regenerates the break."""

    def __init__(self, category, *args, **kwargs):
        super(BreakingTeamsForm, self).__init__(*args, **kwargs)
        self.category = category
        self._prefetch_breakingteams()
        self._create_and_initialise_fields()

    @staticmethod
    def _fieldname_remark(team):  # Team not BreakingTeam
        return 'remark_%(team)d' % {'team': team.id}

    def get_remark_field(self, team):  # Team not BreakingTeam
        return self[self._fieldname_remark(team)].as_widget(attrs={'class': 'form-control'})

    def _bt(self, team):
        return self._bts_by_team_id[team.id]

    def _prefetch_breakingteams(self):
        self._bts_by_team_id = {bt.team_id: bt for bt in self.category.breakingteam_set.all()}

    def _create_and_initialise_fields(self):
        """Dynamically generate fields, one Select for each BreakingTeam."""
        for team in self.category.breaking_teams.all():
            self.fields[self._fieldname_remark(team)] = OptionalChoiceField(choices=BreakingTeam.REMARK_CHOICES, required=False)
            try:
                self.initial[self._fieldname_remark(team)] = self._bt(team).remark
            except KeyError:
                self.initial[self._fieldname_remark(team)] = None

    def save(self):
        for team in self.category.breaking_teams.all():
            try:
                bt = self._bt(team)
            except KeyError:
                continue
            bt.remark = self.cleaned_data[self._fieldname_remark(team)]
            bt.save()
