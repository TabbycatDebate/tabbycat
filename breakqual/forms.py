from django import forms

from utils.forms import OptionalChoiceField

from .models import BreakingTeam
from .breaking import get_breaking_teams

# ==============================================================================
# Break eligbility form
# ==============================================================================


class BreakEligibilityForm(forms.Form):
    """Sets which teams are eligible for the break."""

    def __init__(self, tournament, *args, **kwargs):
        super(BreakEligibilityForm, self).__init__(*args, **kwargs)
        self.tournament = tournament
        self._create_and_initialise_fields()

    @staticmethod
    def _fieldname_eligibility(team):
        return 'eligibility_%(team)d' % {'team': team.id}

    def _create_and_initialise_fields(self):
        """Dynamically generate fields, one ModelMultipleChoiceField for each
        Team."""
        for team in self.tournament.team_set.all():
            self.fields[self._fieldname_eligibility(team)] = forms.ModelMultipleChoiceField(
                queryset=self.tournament.breakcategory_set.all(), widget=forms.CheckboxSelectMultiple,
                required=False)
            self.initial[self._fieldname_eligibility(team)] = team.break_categories.all()

    def save(self):
        for team in self.tournament.team_set.all():
            team.break_categories = self.cleaned_data[self._fieldname_eligibility(team)]
            team.save()

    def team_iter(self):
        for team in self.tournament.team_set.all():
            yield team, self[self._fieldname_eligibility(team)]


# ==============================================================================
# Breaking teams form
# ==============================================================================

class BreakingTeamsForm(forms.Form):
    """Updates the remarks on breaking teams and regenerates the break."""

    def __init__(self, category, *args, **kwargs):
        super(BreakingTeamsForm, self).__init__(*args, **kwargs)
        self.category = category
        self._create_and_initialise_fields()
        self._generate_standings()

    @staticmethod
    def _fieldname_remark(team):  # Team not BreakingTeam
        return 'remark_%(team)d' % {'team': team.id}

    def _bt(self, team):
        return team.breakingteam_set.get(break_category=self.category)

    def _create_and_initialise_fields(self):
        """Dynamically generate fields, one Select for each BreakingTeam."""
        for team in self.category.breaking_teams.all():
            self.fields[self._fieldname_remark(team)] = OptionalChoiceField(choices=BreakingTeam.REMARK_CHOICES, required=False)
            try:
                self.initial[self._fieldname_remark(team)] = self._bt(team).remark
            except BreakingTeam.DoesNotExist:
                self.initial[self._fieldname_remark(team)] = None

    def _generate_standings(self):
        self._standings = get_breaking_teams(self.category, include_all=True, include_categories=True)

    def save(self):
        for team in self.category.breaking_teams.all():
            try:
                bt = self._bt(team)
            except BreakingTeam.DoesNotExist:
                continue
            bt.remark = self.cleaned_data[self._fieldname_remark(team)]
            bt.save()

    def metrics_info(self):
        return self._standings.metrics_info()

    def team_iter(self):
        for standing in self._standings:
            yield standing, self[self._fieldname_remark(standing.team)]
