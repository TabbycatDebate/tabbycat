from django import template
from django.utils.safestring import mark_safe

from options.utils import use_team_code_names
from utils.misc import reverse_tournament

register = template.Library()


@register.simple_tag
def team_record_link(team, admin, tournament=None, style=True):
    """Team record links are used often, so this template tag just reduces
    clutter in templates, in particular in translated strings."""

    if not team:
        return ""

    if not tournament:
        tournament = team.tournament

    if use_team_code_names(tournament, admin):
        name = team.code_name
    else:
        name = team.short_name

    if admin:
        url = reverse_tournament('participants-team-record', tournament, kwargs={'pk': team.pk})
    else:
        url = reverse_tournament('participants-public-team-record', tournament, kwargs={'pk': team.pk})

    classes = 'class="list-group-item-text alert-link"' if style else ''

    return mark_safe("""<a href="%(url)s" %(style)s>%(name)s</a>""" % {'url': url, 'style': classes, 'name': name})


@register.simple_tag
def adj_record_link(adj, admin, tournament=None):

    if not adj:
        return ""

    if not tournament:
        tournament = getattr(adj, 'tournament', None)

    if not tournament: # Still no tournament
        return ""

    if admin:
        url = reverse_tournament('participants-adjudicator-record', tournament, kwargs={'pk': adj.pk})
    else:
        url = reverse_tournament('participants-public-adjudicator-record', tournament, kwargs={'pk': adj.pk})

    return mark_safe(url)
