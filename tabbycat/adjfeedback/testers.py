"""Works out which adjudicators were tested in which rounds.

An adjudicator is a *tester* if they are on the adjudication core, or if they
have been marked as one. An adjudicator counts as *tested* in a round when a
tester sat on their panel that round.
"""

from django.db.models import Q

from adjallocation.models import DebateAdjudicator


def tester_ids(tournament):
    """Returns the ids of every adjudicator who tests others."""
    return set(tournament.adjudicator_set.filter(
        Q(adj_core=True) | Q(is_tester=True),
    ).values_list('id', flat=True))


def get_tested_rounds(tournament):
    """Returns {adjudicator_id: {round_id, ...}} for rounds in which a tester
    sat on that adjudicator's panel. Nobody is tested by their own presence."""
    testers = tester_ids(tournament)
    if not testers:
        return {}

    panels = {}
    for da in DebateAdjudicator.objects.filter(
        debate__round__tournament=tournament,
    ).select_related('debate'):
        panels.setdefault(da.debate_id, []).append(da)

    tested = {}
    for allocations in panels.values():
        panel_testers = {da.adjudicator_id for da in allocations} & testers
        if not panel_testers:
            continue
        for da in allocations:
            if panel_testers - {da.adjudicator_id}:
                tested.setdefault(da.adjudicator_id, set()).add(da.debate.round_id)

    return tested
