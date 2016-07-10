import logging
from warnings import warn

from .models import DebateAdjudicator

logger = logging.getLogger(__name__)


def populate_allocations(debates, attrname="_adjudicators"):
    """Sets an attribute with name `attrname` (default `_adjudicators`) on each
    debate in `debates`, each one being an AdjudicatorAllocation for that
    debate. This can be used for efficiency, since it retrieves all of the
    information in bulk in a single SQL query. Operates in-place.
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


class AdjudicatorAllocation:
    """Class for handling the adjudicators on a panel."""

    POSITION_CHAIR = 'c'
    POSITION_ONLY = 'o'
    POSITION_PANELLIST = 'p'
    POSITION_TRAINEE = 't'

    def __init__(self, debate, chair=None, panellists=None, trainees=None, from_db=False):
        self.debate = debate

        if from_db:
            if chair or panellists or trainees:
                warn("The chair, panellists and trainees arguments are ignored when from_db is used.")
            self.chair = None
            self.panellists = []
            self.trainees = []
            for a in self.debate.debateadjudicator_set.prefetch_related('adjudicator').all():
                if a.type == DebateAdjudicator.TYPE_CHAIR:
                    self.chair = a.adjudicator
                elif a.type == DebateAdjudicator.TYPE_PANEL:
                    self.panellists.append(a.adjudicator)
                elif a.type == DebateAdjudicator.TYPE_TRAINEE:
                    self.trainees.append(a.adjudicator)

        else:
            self.chair = chair
            self.panellists = panellists or []
            self.trainees = trainees or []

    def __len__(self):
        return (0 if self.chair is None else 1) + len(self.panellists) + len(self.trainees)

    def __str__(self):
        items = [str(getattr(x, "name", x)) for x in self.all()]
        return ", ".join(items)

    def __repr__(self):
        result = "<AdjudicatorAllocation for "
        try:
            result += self.debate.matchup
        except AttributeError:
            result += str(self.debate)
        result += ": "
        try:
            result += self.chair.name
        except AttributeError:
            result += str(self.chair)
        result += "; " + ", ".join([p.name for p in self.panellists])
        result += "; " + ", ".join([t.name for t in self.trainees])
        result += ">"
        return result

    def __contains__(self, item):
        return item == self.chair or item in self.panellists or item in self.trainees

    def __eq__(self, other):
        return self.debate == other.debate and \
            self.chair == other.chair and \
            set(self.panellists) == set(other.panellists) and \
            set(self.trainees) == set(other.trainees)

    # ==========================================================================
    # Booleans and other quick properties
    # ==========================================================================

    @property
    def has_chair(self):
        return self.chair is not None

    @property
    def is_panel(self):
        return len(self.panellists) > 0

    @property
    def valid(self):
        return self.has_chair and len(self.panellists) % 2 == 0

    @property
    def num_voting(self):
        return (0 if self.chair is None else 1) + len(self.panellists)

    # ==========================================================================
    # Iterators
    # ==========================================================================

    def voting(self):
        """Iterates through voting members of the panel."""
        if self.chair is not None:
            yield self.chair
        for a in self.panellists:
            yield a

    def all(self):
        """Iterates through all members of the panel."""
        for a in self.voting():
            yield a
        for a in self.trainees:
            yield a

    def with_positions(self):
        """Iterates through 2-tuples `(adj, type)`, where `type` is one of the
        `AdjudicatorAllocation.POSITION_*` constants (`CHAIR`, `ONLY`,
        `PANELLIST` or `TRAINEE`).

        Note that the `AdjudicatorAllocation.POSITION_*` constants are not
        necessarily the same as the `DebateAdjudicator.TYPE_*` constants."""

        if self.chair is not None:
            yield self.chair, self.POSITION_CHAIR if self.is_panel else self.POSITION_ONLY
        for a in self.panellists:
            yield a, self.POSITION_PANELLIST
        for a in self.trainees:
            yield a, self.POSITION_TRAINEE

    def with_debateadj_types(self):
        if self.chair is not None:
            yield self.chair, DebateAdjudicator.TYPE_CHAIR
        for a in self.panellists:
            yield a, DebateAdjudicator.TYPE_PANEL
        for a in self.trainees:
            yield a, DebateAdjudicator.TYPE_TRAINEE

    # ==========================================================================
    # Database operations
    # ==========================================================================

    def delete(self):
        """Delete existing, current allocation"""
        self.debate.debateadjudicator_set.all().delete()
        self.chair = None
        self.panellists = []
        self.trainees = []

    def save(self):
        self.debate.debateadjudicator_set.exclude(adjudicator__in=self.all()).delete()
        for adj, t in self.with_debateadj_types():
            if not adj:
                continue
            _, created = DebateAdjudicator.objects.update_or_create(debate=self.debate, adjudicator=adj,
                    defaults={'type': t})
            logger.info("updating: %s, %s, %s, created = %s" % (self.debate, adj, t, created))

    # ==========================================================================
    # Deprecated
    # ==========================================================================

    @property
    def list(self):
        warn("AdjudicatorAllocation.list is deprecated, use AdjudicatorAllocation.voting() instead", stacklevel=2)
        a = [self.chair]
        a.extend(self.panellists)
        return a

    def __iter__(self):
        warn("AdjudicatorAllocation.__iter__() is deprecated, use .with_positions() or .with_debateadj_types() instead", stacklevel=2)
        if self.chair is not None:
            yield DebateAdjudicator.TYPE_CHAIR, self.chair
        for a in self.panellists:
            yield DebateAdjudicator.TYPE_PANEL, a
        for a in self.trainees:
            yield DebateAdjudicator.TYPE_TRAINEE, a

    @property
    def panel(self):
        warn("AdjudicatorAllocation.panel is deprecated, use AdjudicatorAllocation.panellists instead", stacklevel=2)
        return self.panellists
