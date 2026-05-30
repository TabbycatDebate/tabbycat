from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from dynamic_preferences.forms import preference_form_builder, PreferenceForm

from .preferences import tournament_preferences_registry


class TournamentPreferenceForm(PreferenceForm):
    registry = tournament_preferences_registry

    def clean(self):
        super().clean()
        section, first_pref = self.manager.parse_lookup(next(iter(self.cleaned_data.keys())))
        t = self.manager.instance

        def get_pref(name, section=section):
            return self.cleaned_data.get(section + "__" + name) if (section + "__" + name) in self.cleaned_data else t.pref(name)

        score_range_msg = _("Minimum score must be less than maximum score")

        if section == 'scoring':
            if get_pref('score_min') > get_pref('score_max'):
                raise ValidationError({'scoring__score_min': score_range_msg, 'scoring__score_max': score_range_msg})

            if get_pref('reply_score_min') > get_pref('reply_score_max'):
                raise ValidationError({'scoring__reply_score_min': score_range_msg, 'scoring__reply_score_max': score_range_msg})

        elif section == 'draw_rules':
            if get_pref('draw_side_allocations') != 'preallocated' and get_pref('draw_odd_bracket') in ['intermediate1', 'intermediate2']:
                raise ValidationError({'draw_rules__draw_odd_bracket': _("Intermediate 1 or 2 require preallocated sides")})

            if get_pref('draw_avoid_conflicts') != 'graph_one' and get_pref('draw_odd_bracket') in ['pullup_lowest_ds_rank', 'pullup_lowest_ds_rank_npulls']:
                raise ValidationError({'draw_rules__draw_odd_bracket': _("Draw strength pullups require 'Minimum cost matching (including pullups)' as the conflict avoidance method")})

            if get_pref('draw_avoid_conflicts') != 'one_up_one_down' and 'intermediate' in get_pref('draw_odd_bracket'):
                raise ValidationError({'draw_rules__draw_odd_bracket': _("Intermediate-type pullups require 'One-up-one-down' as the conflict avoidance method")})

        elif section == 'debate_rules':
            if get_pref('teams_in_debate') == 4 and (get_pref('ballots_per_debate_prelim') == 'per-adj' or get_pref('ballots_per_debate_elim') == 'per-adj'):
                raise ValidationError({'debate_rules__teams_in_debate': _("Four-team formats require consensus ballots")})

        elif section == 'feedback':
            adj_min_score = get_pref('adj_min_score')
            adj_max_score = get_pref('adj_max_score')
            if adj_min_score > adj_max_score:
                raise ValidationError({'feedback__adj_min_score': score_range_msg, 'feedback__adj_max_score': score_range_msg})
            adj_score_step = get_pref('adj_score_step')
            if adj_score_step is not None:
                if adj_score_step <= 0:
                    raise ValidationError({'feedback__adj_score_step': _("Score step must be greater than 0.")})
                if adj_score_step > adj_max_score:
                    raise ValidationError({'feedback__adj_score_step': _(
                        "Score step (%(step)s) cannot be greater than the maximum score (%(max)s).") % {
                            'step': adj_score_step, 'max': adj_max_score}})

        elif section == 'data_entry':
            if get_pref('public_use_password') and len(get_pref('public_password')) == 0:
                raise ValidationError({'data_entry__public_password': _("Must set a password if using a password is enabled")})

        elif section == 'ui_options':
            if get_pref('team_code_names') not in ['off', 'all-tooltips'] and get_pref('show_team_institutions'):
                raise ValidationError({'ui_options__show_team_institutions': _("Showing team institutions defeats the purpose of code names")})

        return self.cleaned_data


def tournament_preference_form_builder(instance, preferences=[], **kwargs):
    return preference_form_builder(
        TournamentPreferenceForm, preferences, model={'instance': instance}, **kwargs)
