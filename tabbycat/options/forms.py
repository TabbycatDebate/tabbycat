from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from dynamic_preferences.forms import GlobalPreferenceForm, preference_form_builder, PreferenceForm

from .preferences import global_preferences_registry, tournament_preferences_registry


class TournamentPreferenceForm(PreferenceForm):
    registry = tournament_preferences_registry

    def clean(self):
        super().clean()
        section, first_pref = self.manager.parse_lookup(next(iter(self.cleaned_data.keys())))
        t = self.manager.instance

        def get_pref(name, section=section):
            return self.cleaned_data.get(section + "__" + name) if (section + "__" + name) in self.cleaned_data else t.pref(name)

        score_range_msg = _("Mininum score must be less than maximum score")

        if section == 'scoring':
            if get_pref('score_min') > get_pref('score_max'):
                raise ValidationError({'scoring__score_min': score_range_msg, 'scoring__score_max': score_range_msg})

            if get_pref('reply_score_min') > get_pref('reply_score_max'):
                raise ValidationError({'scoring__reply_score_min': score_range_msg, 'scoring__reply_score_max': score_range_msg})

        elif section == 'draw_rules':
            if get_pref('draw_side_allocations') != 'preallocated' and get_pref('draw_odd_bracket') in ['intermediate1', 'intermediate2']:
                raise ValidationError({'draw_rules__draw_odd_bracket': _("Intermediate 1 or 2 require preallocated sides")})

        elif section == 'debate_rules':
            if get_pref('teams_in_debate') == 4 and (get_pref('ballots_per_debate_prelim') == 'per-adj' or get_pref('ballots_per_debate_elim') == 'per-adj'):
                raise ValidationError({'debate_rules__teams_in_debate': _("Four-team formats require consensus ballots")})

        elif section == 'feedback':
            if get_pref('adj_min_score') > get_pref('adj_max_score'):
                raise ValidationError({'feedback__adj_min_score': score_range_msg, 'feedback__adj_max_score': score_range_msg})

        elif section == 'data_entry':
            if get_pref('public_use_password') and len(get_pref('public_password')) == 0:
                raise ValidationError({'data_entry__public_password': _("Must set a password if using a password is enabled")})

        elif section == 'ui_options':
            if get_pref('team_code_names') not in ['off', 'all-tooltips'] and get_pref('show_team_institutions'):
                raise ValidationError({'ui_options__show_team_institutions': _("Showing team institutions defeats the purpose of code names")})

        return self.cleaned_data


def tournament_preference_form_builder(instance, preferences=[], **kwargs):
    if kwargs.get('section') in [str(s) for s in global_preferences_registry.sections()]:
        # Check for global preferences
        return preference_form_builder(GlobalPreferenceForm, preferences, **kwargs)

    return preference_form_builder(
        TournamentPreferenceForm, preferences, model={'instance': instance}, **kwargs)
