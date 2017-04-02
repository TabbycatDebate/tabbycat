import os
import re

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from tournaments.utils import get_position_name

register = template.Library()
STATIC_PATH = settings.MEDIA_ROOT
version_cache = {}

rx = re.compile(r'^(.*)\.(.*?)$')


@register.simple_tag
def version(path_string, base_url=settings.MEDIA_URL):

    if not hasattr(
            settings,
            'ENABLE_MEDIA_VERSIONING') or not settings.ENABLE_MEDIA_VERSIONING:
        return base_url + path_string

    try:
        if path_string in version_cache:
            mtime = version_cache[path_string]
        else:
            mtime = os.path.getmtime(os.path.join(settings.MEDIA_ROOT,
                                                  path_string))
            version_cache[path_string] = mtime

        return base_url + rx.sub(r'\1.%d.\2' % mtime, path_string)
    except:
        return base_url + path_string


# TODO: deprecate when old allocations UI is
@register.simple_tag
def team_status_classes(team):
    classes = list()
    if team.region is not None:
        classes.append("region-%s" % team.region.id)
    for category in team.break_categories_nongeneral.order_by('priority'):
        classes.append("breakcategory-" + category.slug)
    return " ".join(classes)


@register.simple_tag
def debate_draw_status_class(debate):
    if debate.aff_team and debate.aff_team.type == 'B':
        return "active text-muted"
    elif debate.neg_team and debate.neg_team.type == 'B':
        return "active text-muted"
    elif debate.result_status == "P":
        return "active text-muted"
    elif debate.confirmed_ballot and debate.confirmed_ballot.forfeit:
        return "active text-muted"

    return ""


@register.simple_tag
def tournament_side_names(tournament, name_type):
    side_names = [get_position_name(tournament, 'aff', name_type),
                  get_position_name(tournament, 'neg', name_type)]
    print(side_names)
    return side_names


class RoundURLNode(template.Node):
    def __init__(self, view_name, round=None, args=[]):
        self.view_name = view_name
        self.round = round
        self.args = args

    def render(self, context):
        round = self.round.resolve(context) if self.round else context['round']
        args = [round.tournament.slug, round.seq]
        args.extend(a.resolve(context) for a in self.args)
        return reverse(self.view_name, args=args)


class TournamentURLNode(template.Node):
    def __init__(self, view_name, args):
        self.view_name = view_name
        self.args = args

    def render(self, context):
        args = [context['tournament'].slug]
        args.extend(a.resolve(context) for a in self.args)
        args = tuple(args)
        return reverse(self.view_name, args=args)


class TournamentAbsoluteURLNode(TournamentURLNode):
    def render(self, context):
        path = super(TournamentAbsoluteURLNode, self).render(context)
        return context['request'].build_absolute_uri(path)


@register.tag
def round_url(parser, token):
    bits = token.split_contents()
    if len(bits) >= 3:
        round = parser.compile_filter(bits[2])
        args = [parser.compile_filter(b) for b in bits[3:]]
    else:
        round = None
        args = []
    return RoundURLNode(bits[1], round, args)


@register.tag
def tournament_url(parser, token):
    bits = token.split_contents()
    args = [parser.compile_filter(b) for b in bits[2:]]
    return TournamentURLNode(bits[1], args)


@register.tag
def tournament_absurl(parser, token):
    bits = token.split_contents()
    args = [parser.compile_filter(b) for b in bits[2:]]
    return TournamentAbsoluteURLNode(bits[1], args)


@register.filter
def next_value(value, arg):
    try:
        return value[int(arg) + 1]
    except:
        return None


@register.filter
def prev_value(value, arg):
    try:
        return value[int(arg) - 1]
    except:
        return None


@register.filter(name='times')
def times(number):
    return list(range(number))


@register.simple_tag
def divide_to_int(number_a, number_b):
    try:
        return int(int(number_a) / int(number_b))
    except (ValueError, ZeroDivisionError):
        return None


@register.simple_tag
def percentage(number_a, number_b):
    if number_b > 0:
        return number_a / number_b * 100
    else:
        return 0
