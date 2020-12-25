import os
import re

from django import template
from django.conf import settings
from django.template.base import kwarg_re, TemplateSyntaxError, Variable
from django.template.defaulttags import URLNode

from tournaments.utils import get_side_name

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
    except Exception:
        return base_url + path_string


@register.simple_tag
def tournament_side_names(tournament, name_type):
    side_names = [get_side_name(tournament, 'aff', name_type),
                  get_side_name(tournament, 'neg', name_type)]
    return side_names


@register.simple_tag
def debate_team_side_name(debate_team, tournament):
    # If returned directly from the object it will have to lookup tournament
    return debate_team.get_side_name(tournament)


class TournamentURLNode(URLNode):

    def __init__(self, view_name, args, kwargs, asvar):
        self._args = args      # static copy, as we modify self.args in render()
        self._kwargs = kwargs
        super().__init__(view_name, args, kwargs, asvar)

    def render(self, context):
        """Add the tournament in the context to the arguments, then render as
        usual."""

        # In order to take advantage of the superclass's method, the easiest
        # thing to do is to grab the string we want to insert, and turn it into
        # a (literal) Variable for the superclass. This is a little roundabout,
        # since we're creating a variable only for it to be turned back into
        # the string again, but it's better than copy-pasting the superclass's
        # method itself.
        try:
            tournament_slug = context['tournament'].slug
        except KeyError:
            raise TemplateSyntaxError("tournamenturl can only be used in contexts with a tournament rtf ")
        tournament_slug = Variable("'" + tournament_slug + "'")
        self.args = list(self._args)      # make a copy in case render() gets called multiple times
        self.kwargs = dict(self._kwargs)

        if self.kwargs:
            self.kwargs['tournament_slug'] = tournament_slug
        else:
            self.args.insert(0, tournament_slug)

        return super().render(context)


class TournamentAbsoluteURLNode(TournamentURLNode):
    def render(self, context):
        path = super(TournamentAbsoluteURLNode, self).render(context)
        if self.asvar:
            context[self.asvar] = context['request'].build_absolute_uri(context[self.asvar])
            return path
        else:
            return context['request'].build_absolute_uri(path)


class RoundURLNode(URLNode):

    def __init__(self, view_name, args, kwargs, asvar):
        # Pull round out of the arguments, then let URLNode do the rest.
        if "round" in kwargs:
            self.round = kwargs.pop("round")
        elif len(args) > 0:
            self.round = args.pop(0)
        else:
            self.round = None  # None means take from context
        self._args = args      # static copy, as we modify self.args in render()
        self._kwargs = kwargs

        super().__init__(view_name, args, kwargs, asvar)

    def render(self, context):
        """Add the round to the arguments, then render as usual."""

        # Similar comment as for TournamentURLNode.render()
        round = self.round.resolve(context) if self.round else context['round']
        tournament_slug = Variable("'" + round.tournament.slug + "'")
        round_seq = Variable("'%d'" % round.seq)
        self.args = list(self._args)      # make a copy in case render() gets called multiple times
        self.kwargs = dict(self._kwargs)

        if self.kwargs:
            self.kwargs['tournament_slug'] = tournament_slug
            self.kwargs['round_seq'] = round_seq
        else:
            self.args = [tournament_slug, round_seq] + self.args

        return super().render(context)


def get_url_args(parser, token):
    """Helper function, returns the arguments necessary to construct a URL node.
    This code is copied directly from `url` in django/template/defaulttags.py,
    except that instead of constructing a URL node with the identified
    parameters, it simply returns the parameters in a tuple.
    """

    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument, the name of a url()." % bits[0])
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return viewname, args, kwargs, asvar


@register.tag
def tournamenturl(parser, token):
    """Returns an absolute URL given the matching view for the given tournament,
    or the tournament in the context if no tournament is given."""
    args = get_url_args(parser, token)
    return TournamentURLNode(*args)


@register.tag
def tournament_absurl(parser, token):
    args = get_url_args(parser, token)
    return TournamentAbsoluteURLNode(*args)


@register.tag
def roundurl(parser, token):
    """Returns an absolute URL given the matching view for the given tournament
    and round, or the tournament and round in the context if no tournament is
    given."""
    args = get_url_args(parser, token)
    return RoundURLNode(*args)


@register.filter
def next_value(value, arg):
    try:
        return value[int(arg) + 1]
    except Exception:
        return None


@register.filter
def prev_value(value, arg):
    try:
        return value[int(arg) - 1]
    except Exception:
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
        return number_a / number_b * 100 # Used for progress bars
    else:
        return 0


@register.filter
def subtract(value, arg):
    return value - arg # Used in BP Motion Stats


@register.filter(name='abbreviatename')
def abbreviatename(name):
    """Takes a two-part name and returns an abbreviation like 'E.Lučić'."""
    parts = name.split(" ")
    return "%s.%s" % (parts[0][:5], parts[-1][:5]) # Used for barcodes
