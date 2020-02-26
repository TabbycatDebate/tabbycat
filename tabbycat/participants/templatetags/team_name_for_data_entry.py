from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext

register = template.Library()


@register.simple_tag
def team_name_for_data_entry(team, config):
    """Returns the team name appropriate for data entry.
    `config` is the value returned by options.utils.use_team_code_names_data_entry();
    see that docstring for more details."""
    if not team:
        return ""
    if config == 'code':
        return team.code_name
    elif config == 'both':
        return mark_safe(gettext("%(code_name)s <em>(%(real_name)s)</em>") % {
            'code_name': team.code_name, 'real_name': team.short_name})
    elif config == 'off':
        return team.short_name
