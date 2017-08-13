from django import template
from django.utils.safestring import mark_safe

from utils.misc import reverse_tournament

register = template.Library()


@register.simple_tag
def team_record_link(team, admin):
    """Team record links are used often, so this template tag just reduces
    clutter in templates, in particular in translated strings."""

    if not team:
        return ""

    tournament = team.tournament
    name = team.short_name

    if admin:
        url = reverse_tournament('participants-team-record', tournament, kwargs={'pk': team.pk})
    else:
        url = reverse_tournament('participants-public-team-record', tournament, kwargs={'pk': team.pk})

    return mark_safe("""<a href="%(url)s" class="list-group-item-text">%(name)s</a>""" % {'url': url, 'name': name})
