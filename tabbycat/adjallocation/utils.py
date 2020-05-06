import math
from itertools import combinations, product

from django.utils.translation import gettext as _

from participants.models import Adjudicator, Team

from .conflicts import ConflictsInfo


def adjudicator_conflicts_display(debates):
    """Returns a dict mapping elements (debates) in `debates` to a list of
    strings of explaining conflicts between adjudicators and teams, and
    conflicts between adjudicators and each other."""

    adjudicators = Adjudicator.objects.filter(debateadjudicator__debate__in=debates)
    teams = Team.objects.filter(debateteam__debate__in=debates)
    conflicts = ConflictsInfo(teams=teams, adjudicators=adjudicators)

    conflict_messages = {debate: [] for debate in debates}

    for debate in debates:

        for adj, team in product(debate.adjudicators.all(), debate.teams):

            if conflicts.personal_conflict_adj_team(adj, team):
                conflict_messages[debate].append(("danger", _(
                    "Conflict: <strong>%(adjudicator)s</strong> & <strong>%(team)s</strong> "
                    "(personal)",
                ) % {'adjudicator': adj.name, 'team': team.short_name}))

            for institution in conflicts.conflicting_institutions_adj_team(adj, team):
                conflict_messages[debate].append(("danger", _(
                    "Conflict: <strong>%(adjudicator)s</strong> & <strong>%(team)s</strong> "
                    "via institution <strong>%(institution)s</strong>",
                ) % {
                    'adjudicator': adj.name,
                    'team': team.short_name,
                    'institution': institution.code,
                }))

        for adj1, adj2 in combinations(debate.adjudicators.all(), 2):

            if conflicts.personal_conflict_adj_adj(adj1, adj2):
                conflict_messages[debate].append(("danger", _(
                    "Conflict: <strong>%(adjudicator1)s</strong> & <strong>%(adjudicator2)s</strong> "
                    "(personal)",
                ) % {'adjudicator1': adj1.name, 'adjudicator2': adj2.name}))

            for institution in conflicts.conflicting_institutions_adj_adj(adj1, adj2):
                conflict_messages[debate].append(("warning", _(
                    "Conflict: <strong>%(adjudicator1)s</strong> & <strong>%(adjudicator2)s</strong> "
                    "via institution <strong>%(institution)s</strong>",
                ) % {
                    'adjudicator1': adj1.name,
                    'adjudicator2': adj2.name,
                    'institution': institution.code,
                }))

    return conflict_messages


def percentile(n, percent, key=lambda x: x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not n:
        return None
    k = (len(n)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(n[int(k)])
    d0 = key(n[int(f)]) * (c-k)
    d1 = key(n[int(c)]) * (k-f)
    return d0+d1
