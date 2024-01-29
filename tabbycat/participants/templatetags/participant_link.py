from django import template
from django.utils.safestring import mark_safe

from options.utils import use_team_code_names
from utils.misc import reverse_tournament

register = template.Library()


@register.simple_tag(takes_context=True)
def team_record_link(context, team, admin, style=True):
    """Team record links are used often, so this template tag just reduces
    clutter in templates, in particular in translated strings."""

    if not team or not context['tournament']:
        return ""

    if use_team_code_names(context['tournament'], admin, user=context['user']):
        name = team.code_name
    else:
        name = team.short_name

    if admin:
        url = reverse_tournament('participants-team-record', context['tournament'], kwargs={'pk': team.pk})
    else:
        url = reverse_tournament('participants-public-team-record', context['tournament'], kwargs={'pk': team.pk})

    classes = 'class="list-group-item-text alert-link"' if style else ''

    return mark_safe("""<a href="%(url)s" %(style)s>%(name)s</a>""" % {'url': url, 'style': classes, 'name': name})


@register.simple_tag(takes_context=True)
def adj_record_link(context, adj, admin):

    if not adj or not context['tournament']:
        return ""

    if admin:
        url = reverse_tournament('participants-adjudicator-record', context['tournament'], kwargs={'pk': adj.pk})
    else:
        url = reverse_tournament('participants-public-adjudicator-record', context['tournament'], kwargs={'pk': adj.pk})

    return mark_safe(url)
