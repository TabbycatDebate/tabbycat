from .allocation import AdjudicatorAllocation
from .models import DebateAdjudicator


def populate_allocations(debates):
    """Sets an attribute `_adjudicators` on each debate in `debates`, each one
    being an AdjudicatorAllocation for that debate. This can be used for
    efficiency, since it retrieves all of the information in bulk in a single
    SQL query. Operates in-place.
    """

    debates_by_id = {debate.id: debate for debate in debates}
    for debate in debates:
        debate._adjudicators = AdjudicatorAllocation(debate)

    for debateadj in DebateAdjudicator.objects.filter(debate__in=debates).select_related('adjudicator', 'adjudicator__institution'):
        allocation = debates_by_id[debateadj.debate_id]._adjudicators
        if debateadj.type == DebateAdjudicator.TYPE_CHAIR:
            allocation.chair = debateadj.adjudicator
        elif debateadj.type == DebateAdjudicator.TYPE_PANEL:
            allocation.panellists.append(debateadj.adjudicator)
        elif debateadj.type == DebateAdjudicator.TYPE_TRAINEE:
            allocation.trainees.append(debateadj.adjudicator)
