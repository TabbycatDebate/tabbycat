from django import template
from django.contrib.humanize.templatetags.humanize import ordinal

register = template.Library()


@register.simple_tag
def break_rank(team, round):
    rank = team.break_rank_for_category(round.break_category)
    if rank:
        return "(broke %s)" % ordinal(rank)
    else:
        return None
